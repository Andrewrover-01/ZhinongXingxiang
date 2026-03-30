"""
AI Doctor — disease/pest diagnosis via multimodal RAG.

Endpoints
─────────
POST /ai-doctor/diagnose            submit image + description → diagnosis report
GET  /ai-doctor/records             list current user's diagnosis history
GET  /ai-doctor/records/{id}        get single diagnosis record
"""

import logging
from datetime import datetime
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sse_starlette.sse import EventSourceResponse

_log = logging.getLogger(__name__)
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.limiter import limiter
from app.models.recognition import RecognitionRecord
from app.models.user import User
from app.rag.chain import RAGChain, get_rag_chain
from app.routers.deps import get_current_user
from app.schemas.rag import DiagnoseRequest, DiagnoseResponse
from app.services.rag_service import run_diagnosis, run_diagnosis_stream

router = APIRouter(prefix="/ai-doctor", tags=["AI Doctor"])


# ── Diagnosis ─────────────────────────────────────────────────────────────────

@router.post(
    "/diagnose",
    response_model=DiagnoseResponse,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("20/minute")
async def diagnose(
    request: Request,
    req: DiagnoseRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    chain: RAGChain = Depends(get_rag_chain),
):
    """
    Submit an image URL and optional description.  
    Returns a structured diagnosis report powered by RAG + LLM.
    """
    result = await run_diagnosis(db, req, user_id=current_user.id, chain=chain)
    return DiagnoseResponse(**result)


@router.post("/diagnose/stream")
@limiter.limit("20/minute")
async def diagnose_stream(
    request: Request,
    req: DiagnoseRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    chain: RAGChain = Depends(get_rag_chain),
):
    """
    Submit an image URL and optional description.
    Returns a Server-Sent Events stream of the diagnosis text.
    A final ``data: [DONE]`` event signals stream completion.
    A ``data: [ERROR]`` event is emitted if the stream fails mid-way.
    """

    async def _event_generator():
        try:
            async for chunk in run_diagnosis_stream(
                db, req, user_id=current_user.id, chain=chain
            ):
                yield {"data": chunk}
            yield {"data": "[DONE]"}
        except Exception as exc:
            # Signal the client that an error occurred, then swallow the
            # exception so it does not propagate into sse_starlette's anyio
            # task group and become an ExceptionGroup.
            _log.warning("SSE diagnose stream error: %s", exc, exc_info=True)
            yield {"data": "[ERROR]"}

    return EventSourceResponse(_event_generator())


# ── History ───────────────────────────────────────────────────────────────────

class _RecordOut(DiagnoseResponse):
    """Extends DiagnoseResponse with timestamps for the list view."""

    created_at: datetime  # type: ignore[assignment]


@router.get("/records")
def list_records(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = 0,
    limit: int = 20,
):
    records = (
        db.query(RecognitionRecord)
        .filter(RecognitionRecord.user_id == current_user.id)
        .order_by(RecognitionRecord.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [_record_to_dict(r) for r in records]


@router.get("/records/{record_id}")
def get_record(
    record_id: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    record = (
        db.query(RecognitionRecord)
        .filter(
            RecognitionRecord.id == record_id,
            RecognitionRecord.user_id == current_user.id,
        )
        .first()
    )
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="记录不存在")
    return _record_to_dict(record)


def _record_to_dict(r: RecognitionRecord) -> dict:
    return {
        "record_id": r.id,
        "image_url": r.image_url,
        "description": r.description,
        "crop_type": r.crop_type,
        "diagnosis": r.diagnosis,
        "severity": r.severity,
        "confidence": float(r.confidence) if r.confidence else None,
        "treatment_plan": r.treatment_plan,
        "medicine_suggest": r.medicine_suggest,
        "sources": r.rag_sources or [],
        "llm_model": r.llm_model or "fallback",
        "created_at": r.created_at.isoformat(),
    }
