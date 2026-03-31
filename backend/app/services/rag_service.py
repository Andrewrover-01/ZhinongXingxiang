"""
RAG service — business logic that ties together the chain, DB writes,
and response building.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, AsyncGenerator, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.recognition import PolicyChatHistory, RecognitionRecord
from app.rag.chain import RAGChain, RAGResult, get_rag_chain
from app.rag.vector_store import VectorStore
from app.schemas.rag import DiagnoseRequest, RAGSourceOut


_DIAGNOSIS_SYSTEM = (
    "你是一位专业农作物病虫害诊断专家。"
    "请根据知识库参考资料，对农民描述的症状给出诊断意见。"
    "回答格式：\n"
    "【诊断结果】病害/虫害名称\n"
    "【严重程度】轻度/中度/重度\n"
    "【防治方案】具体操作步骤\n"
    "【推荐药品】药品名称及用量"
)

_POLICY_SYSTEM = (
    "你是一位专业农业政策顾问，熟悉国家及地方农业补贴、土地、保险等政策。"
    "请根据知识库参考资料，用通俗易懂的语言回答农民的政策问题。"
    "如政策有时效性，请提示农民以官方最新公告为准。"
)


def _sources_to_schema(result: RAGResult) -> List[RAGSourceOut]:
    return [
        RAGSourceOut(
            id=s.id,
            title=s.title,
            category=s.category,
            snippet=s.snippet,
            distance=s.distance,
        )
        for s in result.sources
    ]


def _parse_severity(answer: str) -> Optional[str]:
    if "重度" in answer or "严重" in answer:
        return "severe"
    if "中度" in answer:
        return "moderate"
    if "轻度" in answer:
        return "mild"
    return None


def _parse_diagnosis_title(answer: str) -> str:
    for line in answer.splitlines():
        if "诊断结果" in line:
            return line.replace("【诊断结果】", "").strip()
    return answer[:50]


def _parse_treatment(answer: str) -> str:
    lines = answer.splitlines()
    capture = False
    parts = []
    for line in lines:
        if "防治方案" in line:
            capture = True
            rest = line.replace("【防治方案】", "").strip()
            if rest:
                parts.append(rest)
            continue
        if capture:
            if line.startswith("【"):
                break
            parts.append(line)
    return "\n".join(parts).strip() or answer


def _parse_medicine(answer: str) -> Optional[str]:
    for line in answer.splitlines():
        if "推荐药品" in line:
            return line.replace("【推荐药品】", "").strip()
    return None


# ── AI Doctor ─────────────────────────────────────────────────────────────────

async def run_diagnosis(
    db: Session,
    request: DiagnoseRequest,
    user_id: str,
    chain: Optional[RAGChain] = None,
) -> Dict[str, Any]:
    """Run the disease-diagnosis RAG chain and persist the record."""
    rag = chain or get_rag_chain()
    query = f"{request.crop_type or ''}作物 {request.description or ''} 图片诊断".strip()

    result: RAGResult = await rag.arun(
        query,
        category_filter="disease",
        system_prompt=_DIAGNOSIS_SYSTEM,
    )

    diagnosis = _parse_diagnosis_title(result.answer)
    treatment = _parse_treatment(result.answer)
    severity = _parse_severity(result.answer)
    medicine = _parse_medicine(result.answer)
    sources_json = [
        {"id": s.id, "title": s.title, "snippet": s.snippet}
        for s in result.sources
    ]

    record = RecognitionRecord(
        id=str(uuid.uuid4()),
        user_id=user_id,
        farmland_id=request.farmland_id,
        image_url=request.image_url,
        description=request.description,
        crop_type=request.crop_type,
        diagnosis=diagnosis,
        severity=severity,
        confidence=Decimal("0.8500"),
        treatment_plan=treatment,
        medicine_suggest=medicine,
        rag_sources=sources_json,
        llm_model="gpt-4o-mini" if result.sources else "fallback",
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "record_id": record.id,
        "diagnosis": diagnosis,
        "severity": severity,
        "confidence": float(record.confidence or 0),
        "treatment_plan": treatment,
        "medicine_suggest": medicine,
        "sources": _sources_to_schema(result),
        "llm_model": record.llm_model,
    }


# ── Policy chat ────────────────────────────────────────────────────────────────

async def run_policy_chat_stream(
    db: Session,
    session_id: str,
    user_id: str,
    message: str,
    chain: Optional[RAGChain] = None,
) -> AsyncGenerator[str, None]:
    """Persist the user message, run RAG, stream the answer."""
    # Persist user message
    user_msg = PolicyChatHistory(
        id=str(uuid.uuid4()),
        user_id=user_id,
        session_id=session_id,
        role="user",
        content=message,
    )
    db.add(user_msg)
    db.commit()

    # Collect streamed answer
    rag = chain or get_rag_chain()
    full_answer = ""
    async for chunk in rag.astream(
        message, category_filter="policy", system_prompt=_POLICY_SYSTEM
    ):
        full_answer += chunk
        yield chunk

    # Persist assistant message
    assistant_msg = PolicyChatHistory(
        id=str(uuid.uuid4()),
        user_id=user_id,
        session_id=session_id,
        role="assistant",
        content=full_answer,
    )
    db.add(assistant_msg)
    db.commit()


async def run_diagnosis_stream(
    db: Session,
    request: DiagnoseRequest,
    user_id: str,
    chain: Optional[RAGChain] = None,
) -> AsyncGenerator[str, None]:
    """
    Run the disease-diagnosis RAG chain with SSE streaming.

    Yields answer text chunks. After all chunks are yielded, persists the
    RecognitionRecord to the database.
    """
    rag = chain or get_rag_chain()
    query = f"{request.crop_type or ''}作物 {request.description or ''} 图片诊断".strip()

    full_answer = ""
    async for chunk in rag.astream(
        query,
        category_filter="disease",
        system_prompt=_DIAGNOSIS_SYSTEM,
    ):
        full_answer += chunk
        yield chunk

    # Persist after streaming completes
    diagnosis = _parse_diagnosis_title(full_answer)
    treatment = _parse_treatment(full_answer)
    severity = _parse_severity(full_answer)
    medicine = _parse_medicine(full_answer)

    record = RecognitionRecord(
        id=str(uuid.uuid4()),
        user_id=user_id,
        farmland_id=request.farmland_id,
        image_url=request.image_url,
        description=request.description,
        crop_type=request.crop_type,
        diagnosis=diagnosis,
        severity=severity,
        confidence=Decimal("0.8500"),
        treatment_plan=treatment,
        medicine_suggest=medicine,
        rag_sources=[],
        llm_model="gpt-4o-mini-stream",
    )
    db.add(record)
    db.commit()


def get_session_messages(
    db: Session,
    session_id: str,
    user_id: str,
    page: int = 1,
    page_size: int = 20,
) -> tuple[List[PolicyChatHistory], int]:
    """Return a paginated list of messages and the total count."""
    query = (
        db.query(PolicyChatHistory)
        .filter(
            PolicyChatHistory.session_id == session_id,
            PolicyChatHistory.user_id == user_id,
        )
        .order_by(PolicyChatHistory.created_at)
    )
    total = query.count()
    messages = query.offset((page - 1) * page_size).limit(page_size).all()
    return messages, total


def list_sessions(db: Session, user_id: str) -> List[Dict[str, Any]]:
    """Return one summary dict per session_id."""
    rows = (
        db.query(PolicyChatHistory)
        .filter(PolicyChatHistory.user_id == user_id)
        .order_by(PolicyChatHistory.created_at.desc())
        .all()
    )
    seen: Dict[str, Dict[str, Any]] = {}
    for row in rows:
        if row.session_id not in seen:
            seen[row.session_id] = {
                "session_id": row.session_id,
                "message_count": 0,
                "last_message": row.content[:80],
                "last_at": row.created_at.isoformat(),
            }
        seen[row.session_id]["message_count"] += 1
    return list(seen.values())


def delete_session(db: Session, session_id: str, user_id: str) -> int:
    deleted = (
        db.query(PolicyChatHistory)
        .filter(
            PolicyChatHistory.session_id == session_id,
            PolicyChatHistory.user_id == user_id,
        )
        .delete()
    )
    db.commit()
    return deleted
