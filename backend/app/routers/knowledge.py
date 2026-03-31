"""
Knowledge document CRUD + semantic search API.

Endpoints
─────────
GET    /knowledge/               list with optional category filter + pagination
POST   /knowledge/               create new document (auth required)
GET    /knowledge/search         hybrid semantic search
GET    /knowledge/{id}           get single document
PUT    /knowledge/{id}           update document (auth required)
DELETE /knowledge/{id}           delete document (auth required)
"""

from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.rag.vector_store import VectorStore, get_vector_store
from app.routers.deps import get_current_user
from app.schemas.knowledge import (
    KnowledgeCategory,
    KnowledgeCreate,
    KnowledgeListResponse,
    KnowledgeResponse,
    KnowledgeSearchResult,
    KnowledgeUpdate,
)
from app.services.knowledge import (
    create_knowledge,
    delete_knowledge,
    get_knowledge,
    list_knowledge,
    update_knowledge,
)

router = APIRouter(prefix="/knowledge", tags=["Knowledge"])


# ── Helpers ───────────────────────────────────────────────────────────────────

def _vs() -> VectorStore:
    return get_vector_store()


# ── Endpoints ─────────────────────────────────────────────────────────────────


@router.get("/", response_model=KnowledgeListResponse)
def list_docs(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    category: Optional[KnowledgeCategory] = Query(None, description="disease | policy | technique | pest | weather"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    total, items = list_knowledge(db, category=category.value if category else None, skip=skip, limit=limit)
    return KnowledgeListResponse(total=total, items=items)


@router.get("/search", response_model=List[KnowledgeSearchResult])
def search_docs(
    current_user: Annotated[User, Depends(get_current_user)],
    q: str = Query(..., min_length=1, description="搜索关键词"),
    category: Optional[KnowledgeCategory] = Query(None),
    n: int = Query(5, ge=1, le=20),
    vs: VectorStore = Depends(_vs),
):
    from app.rag.retriever import HybridRetriever

    retriever = HybridRetriever(vs, n_semantic=20, n_results=n)
    where = {"category": category.value} if category else None
    results = retriever.retrieve(q, where=where)
    return [
        KnowledgeSearchResult(
            id=r.id,
            title=r.metadata.get("title", r.id),
            category=r.metadata.get("category", ""),
            snippet=r.document[:200],
            crop_types=r.metadata.get("crop_types") or None,
            region=r.metadata.get("region") or None,
            source=r.metadata.get("source") or None,
            similarity=round(1.0 - r.distance, 4),
        )
        for r in results
    ]


@router.get("/{doc_id}", response_model=KnowledgeResponse)
def get_doc(
    doc_id: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    doc = get_knowledge(db, doc_id)
    if doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在")
    return doc


@router.post("/", response_model=KnowledgeResponse, status_code=status.HTTP_201_CREATED)
def create_doc(
    data: KnowledgeCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    vs: VectorStore = Depends(_vs),
):
    doc = create_knowledge(db, data, uploader_id=current_user.id, vs=vs)
    return doc


@router.put("/{doc_id}", response_model=KnowledgeResponse)
def update_doc(
    doc_id: str,
    data: KnowledgeUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    vs: VectorStore = Depends(_vs),
):
    doc = get_knowledge(db, doc_id)
    if doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在")
    if doc.upload_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限修改该文档")
    return update_knowledge(db, doc_id, data, vs=vs)


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_doc(
    doc_id: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    vs: VectorStore = Depends(_vs),
):
    doc = get_knowledge(db, doc_id)
    if doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在")
    if doc.upload_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限删除该文档")
    delete_knowledge(db, doc_id, vs=vs)
