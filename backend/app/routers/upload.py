import os
import re
import uuid
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from app.core.config import settings
from app.models.user import User
from app.routers.deps import get_current_user

router = APIRouter(prefix="/upload", tags=["文件上传"])

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}

# Magic byte signatures for each allowed MIME type.
# Each entry is a list of (offset, expected_bytes) pairs — ALL must match.
_MAGIC: dict[str, list[tuple[int, bytes]]] = {
    "image/jpeg": [(0, b"\xff\xd8\xff")],
    "image/png":  [(0, b"\x89PNG\r\n\x1a\n")],
    "image/webp": [(0, b"RIFF"), (8, b"WEBP")],
    "image/gif":  [(0, b"GIF87a"), (0, b"GIF89a")],  # first matching slice is accepted
}


def _magic_matches(content: bytes, content_type: str) -> bool:
    """Return True if the file content matches the expected magic bytes for *content_type*."""
    rules = _MAGIC.get(content_type)
    if rules is None:
        return False
    if content_type == "image/gif":
        # GIF has two possible signatures; accept either
        return any(content[off: off + len(sig)] == sig for off, sig in rules)
    # All (offset, bytes) pairs must match
    return all(content[off: off + len(sig)] == sig for off, sig in rules)


@router.post("/image", status_code=status.HTTP_201_CREATED)
async def upload_image(
    file: UploadFile,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """上传图片（用于 AI 医生病害识别等场景）"""
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式 {file.content_type}，请上传 JPG/PNG/WebP/GIF 图片",
        )

    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail="文件大小超过限制（最大 10 MB）")

    # Verify actual file content via magic bytes to prevent Content-Type spoofing
    if not _magic_matches(content, file.content_type):
        raise HTTPException(
            status_code=400,
            detail="文件内容与声明的格式不符，请上传真实的 JPG/PNG/WebP/GIF 图片",
        )

    upload_dir = Path(settings.UPLOAD_DIR) / "images"
    upload_dir.mkdir(parents=True, exist_ok=True)

    ext = Path(file.filename or "image.jpg").suffix or ".jpg"
    filename = f"{uuid.uuid4()}{ext}"
    file_path = upload_dir / filename

    with open(file_path, "wb") as f:
        f.write(content)

    return {
        "filename": filename,
        "url": f"/upload/images/{filename}",
        "size": len(content),
        "content_type": file.content_type,
    }


@router.get("/images/{filename}")
async def serve_image(filename: str):
    """获取已上传的图片"""
    # Only allow safe UUID-based filenames with known image extensions
    if not re.match(r"^[a-f0-9\-]{36}\.(jpg|jpeg|png|gif|webp)$", filename, re.IGNORECASE):
        raise HTTPException(status_code=400, detail="无效的文件名")

    upload_base = Path(settings.UPLOAD_DIR).resolve()
    file_path = (upload_base / "images" / filename).resolve()

    # Guard against path traversal: resolved path must stay inside upload dir
    if not str(file_path).startswith(str(upload_base)):
        raise HTTPException(status_code=403, detail="拒绝访问")

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")
    return FileResponse(str(file_path))
