"""
Policy Assistant — agricultural-policy RAG chat with SSE streaming.

Endpoints
─────────
POST   /policy/chat                 send message, receive SSE-streamed answer
GET    /policy/sessions             list current user's chat sessions
GET    /policy/sessions/{session_id} get all messages in a session
DELETE /policy/sessions/{session_id} delete a session
"""

from __future__ import annotations

import json
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sse_starlette.sse import EventSourceResponse  # type: ignore

_log = logging.getLogger(__name__)

from app.core.database import get_db
from app.models.user import User
from app.rag.chain import RAGChain, get_rag_chain
from app.routers.deps import get_current_user
from app.schemas.rag import PolicyChatRequest, PolicyChatMessage, PolicySessionSummary
from app.services.rag_service import (
    delete_session,
    get_session_messages,
    list_sessions,
    run_policy_chat_stream,
)

router = APIRouter(prefix="/policy", tags=["Policy Assistant"])


# ── Chat ──────────────────────────────────────────────────────────────────────

@router.post("/chat")
async def policy_chat(
    req: PolicyChatRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    chain: RAGChain = Depends(get_rag_chain),
):
    """
    Send a policy question and receive an SSE-streamed answer.

    The response is Server-Sent Events; each event has ``data: <chunk>``.
    A final ``data: [DONE]`` event signals stream completion.
    """

    async def _event_generator():
        try:
            async for chunk in run_policy_chat_stream(
                db,
                session_id=req.session_id,
                user_id=current_user.id,
                message=req.message,
                chain=chain,
            ):
                yield {"data": chunk}
            yield {"data": "[DONE]"}
        except Exception as exc:
            # Swallow the exception so it does not propagate into
            # sse_starlette's anyio task-group and become an ExceptionGroup.
            # asyncio.CancelledError is a BaseException (not Exception) so it
            # is still re-raised, letting anyio handle normal cancellation.
            _log.warning("SSE policy chat stream error: %s", exc, exc_info=True)

    return EventSourceResponse(_event_generator())


# ── Session management ────────────────────────────────────────────────────────

@router.get("/sessions")
def get_sessions(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return list_sessions(db, current_user.id)


@router.get("/sessions/{session_id}")
def get_session(
    session_id: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    messages = get_session_messages(db, session_id, current_user.id)
    if not messages:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")
    return [
        {
            "id": m.id,
            "session_id": m.session_id,
            "role": m.role,
            "content": m.content,
            "rag_sources": m.rag_sources,
            "created_at": m.created_at.isoformat(),
        }
        for m in messages
    ]


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_session(
    session_id: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    deleted = delete_session(db, session_id, current_user.id)
    if deleted == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")
