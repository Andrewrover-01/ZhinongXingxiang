"""
Knowledge document DB service (SQLAlchemy CRUD + ChromaDB sync).
"""

from __future__ import annotations

import uuid
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.knowledge import KnowledgeDocument
from app.rag.vector_store import VectorStore, get_vector_store
from app.schemas.knowledge import KnowledgeCreate, KnowledgeUpdate


def _chroma_id(doc_id: str) -> str:
    return f"kb_{doc_id}"


def _to_chroma_doc(doc: KnowledgeDocument) -> dict:
    return {
        "id": _chroma_id(doc.id),
        "document": doc.content,
        "metadata": {
            "title": doc.title,
            "category": doc.category,
            "crop_types": doc.crop_types or "",
            "region": doc.region or "",
            "source": doc.source or "",
            "db_id": doc.id,
        },
    }


# ── CRUD ───────────────────────────────────────────────────────────────────────

def create_knowledge(
    db: Session,
    data: KnowledgeCreate,
    uploader_id: Optional[str] = None,
    vs: Optional[VectorStore] = None,
) -> KnowledgeDocument:
    doc = KnowledgeDocument(
        id=str(uuid.uuid4()),
        title=data.title,
        category=data.category,
        content=data.content,
        source=data.source,
        crop_types=data.crop_types,
        region=data.region,
        summary=data.summary,
        is_verified=data.is_verified,
        upload_by=uploader_id,
    )
    doc.chroma_id = _chroma_id(doc.id)
    db.add(doc)
    db.flush()

    # Sync to vector store
    store = vs or get_vector_store()
    store.add([_to_chroma_doc(doc)])

    db.commit()
    db.refresh(doc)
    return doc


def get_knowledge(db: Session, doc_id: str) -> Optional[KnowledgeDocument]:
    return db.query(KnowledgeDocument).filter(KnowledgeDocument.id == doc_id).first()


def list_knowledge(
    db: Session,
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
) -> tuple[int, List[KnowledgeDocument]]:
    q = db.query(KnowledgeDocument)
    if category:
        q = q.filter(KnowledgeDocument.category == category)
    total = q.count()
    items = q.order_by(KnowledgeDocument.created_at.desc()).offset(skip).limit(limit).all()
    return total, items


def update_knowledge(
    db: Session,
    doc_id: str,
    data: KnowledgeUpdate,
    vs: Optional[VectorStore] = None,
) -> Optional[KnowledgeDocument]:
    doc = get_knowledge(db, doc_id)
    if doc is None:
        return None
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(doc, k, v)
    db.flush()

    # Re-sync vector store if content changed
    if data.content is not None:
        store = vs or get_vector_store()
        store.add([_to_chroma_doc(doc)])

    db.commit()
    db.refresh(doc)
    return doc


def delete_knowledge(
    db: Session,
    doc_id: str,
    vs: Optional[VectorStore] = None,
) -> bool:
    doc = get_knowledge(db, doc_id)
    if doc is None:
        return False
    store = vs or get_vector_store()
    store.delete([_chroma_id(doc_id)])
    db.delete(doc)
    db.commit()
    return True


def bulk_create_knowledge(
    db: Session,
    items: List[KnowledgeCreate],
    vs: Optional[VectorStore] = None,
) -> int:
    """Batch-insert without calling get_vector_store for every item."""
    store = vs or get_vector_store()
    chroma_docs = []
    count = 0
    for data in items:
        doc = KnowledgeDocument(
            id=str(uuid.uuid4()),
            title=data.title,
            category=data.category,
            content=data.content,
            source=data.source,
            crop_types=data.crop_types,
            region=data.region,
            summary=data.summary,
            is_verified=data.is_verified,
        )
        doc.chroma_id = _chroma_id(doc.id)
        db.add(doc)
        chroma_docs.append(_to_chroma_doc(doc))
        count += 1

    db.flush()
    store.add(chroma_docs)
    db.commit()
    return count
