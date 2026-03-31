from __future__ import annotations

import re
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


# ── Shared source reference ───────────────────────────────────────────────────

class RAGSourceOut(BaseModel):
    id: str
    title: str
    category: str
    snippet: str
    distance: float


# ── AI Doctor ─────────────────────────────────────────────────────────────────

class DiagnoseRequest(BaseModel):
    image_url: str = Field(..., max_length=500, description="已上传图片的 URL 或相对路径")
    description: Optional[str] = Field(None, max_length=1000, description="用户文字描述（可选）")
    crop_type: Optional[str] = Field(None, max_length=100)
    farmland_id: Optional[str] = None

    @field_validator("image_url")
    @classmethod
    def validate_image_url(cls, v: str) -> str:
        # Allow only relative upload paths or http(s) URLs; block SSRF via other schemes
        if not (v.startswith("/upload/images/") or re.match(r"^https?://", v)):
            raise ValueError("image_url 必须是 /upload/images/ 路径或 http(s) URL")
        return v


class DiagnoseResponse(BaseModel):
    record_id: str
    diagnosis: str
    severity: Optional[str] = None          # mild | moderate | severe
    confidence: Optional[float] = None       # 0.0 – 1.0
    treatment_plan: str
    medicine_suggest: Optional[str] = None
    sources: List[RAGSourceOut] = []
    llm_model: str


# ── Policy chat ───────────────────────────────────────────────────────────────

class PolicyChatRequest(BaseModel):
    session_id: str = Field(..., description="会话 ID（多轮对话归组）")
    message: str = Field(..., min_length=1, max_length=2000)


class PolicyChatMessage(BaseModel):
    id: str
    session_id: str
    role: str  # user | assistant
    content: str
    rag_sources: Optional[List[RAGSourceOut]] = None
    created_at: str

    model_config = {"from_attributes": True}


class PolicySessionSummary(BaseModel):
    session_id: str
    message_count: int
    last_message: str
    last_at: str
