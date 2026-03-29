from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# ── Create / Update ───────────────────────────────────────────────────────────

class KnowledgeCreate(BaseModel):
    title: str = Field(..., max_length=200)
    # disease | policy | technique | pest | weather
    category: str = Field(..., max_length=50)
    content: str
    source: Optional[str] = Field(None, max_length=200)
    crop_types: Optional[str] = None  # comma-separated, e.g. "水稻,小麦"
    region: Optional[str] = Field(None, max_length=100)
    summary: Optional[str] = None
    is_verified: bool = False


class KnowledgeUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    category: Optional[str] = Field(None, max_length=50)
    content: Optional[str] = None
    source: Optional[str] = Field(None, max_length=200)
    crop_types: Optional[str] = None
    region: Optional[str] = Field(None, max_length=100)
    summary: Optional[str] = None
    is_verified: Optional[bool] = None


# ── Response ──────────────────────────────────────────────────────────────────

class KnowledgeResponse(BaseModel):
    id: str
    title: str
    category: str
    content: str
    source: Optional[str] = None
    crop_types: Optional[str] = None
    region: Optional[str] = None
    summary: Optional[str] = None
    chroma_id: Optional[str] = None
    is_verified: bool
    upload_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class KnowledgeListResponse(BaseModel):
    total: int
    items: List[KnowledgeResponse]


# ── Search ────────────────────────────────────────────────────────────────────

class KnowledgeSearchResult(BaseModel):
    id: str
    title: str
    category: str
    snippet: str  # first 200 chars of content
    crop_types: Optional[str] = None
    region: Optional[str] = None
    source: Optional[str] = None
    similarity: float  # 1 - cosine_distance
