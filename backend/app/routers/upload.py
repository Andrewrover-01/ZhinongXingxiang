import os
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
    file_path = Path(settings.UPLOAD_DIR) / "images" / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")
    return FileResponse(str(file_path))
