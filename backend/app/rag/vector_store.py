"""
ChromaDB wrapper — CRUD + semantic search.

The module keeps a **module-level singleton** so that every FastAPI
request reuses the same client and collection objects.

Usage
-----
>>> from app.rag.vector_store import get_vector_store
>>> vs = get_vector_store()
>>> vs.add([{"id": "doc1", "document": "...", "metadata": {...}}])
>>> results = vs.query("稻瘟病防治方法", n_results=5)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import chromadb

from app.core.config import settings
from app.rag.embeddings import get_embedding_function

logger = logging.getLogger(__name__)

COLLECTION_NAME = "agriculture_knowledge"


@dataclass
class SearchResult:
    id: str
    document: str
    metadata: Dict[str, Any]
    distance: float = 0.0


# ── Module-level singleton ─────────────────────────────────────────────────────

_vector_store: Optional["VectorStore"] = None


def get_vector_store(
    *,
    persist_dir: Optional[str] = None,
    embedding_backend: Optional[str] = None,
    ephemeral: bool = False,
) -> "VectorStore":
    """
    Return (and lazily create) the global VectorStore singleton.

    Parameters
    ----------
    persist_dir:
        Override ``settings.CHROMA_PERSIST_DIR``.
    embedding_backend:
        Override ``settings.CHROMA_EMBEDDING_BACKEND``.
    ephemeral:
        When *True* use an in-memory EphemeralClient (useful in tests).
        This bypasses the singleton so each call returns a fresh store.
    """
    global _vector_store

    if ephemeral:
        return VectorStore(ephemeral=True, embedding_backend=embedding_backend or "mock")

    if _vector_store is None:
        _vector_store = VectorStore(
            persist_dir=persist_dir or settings.CHROMA_PERSIST_DIR,
            embedding_backend=embedding_backend,
        )
    return _vector_store


def reset_vector_store() -> None:
    """Reset the singleton (used in tests)."""
    global _vector_store
    _vector_store = None


# ── VectorStore ────────────────────────────────────────────────────────────────


@dataclass
class VectorStore:
    persist_dir: str = field(default="./chroma_data")
    embedding_backend: Optional[str] = None
    ephemeral: bool = False

    # Internal attributes (not constructor params in the same sense)
    _client: Any = field(init=False, default=None)
    _collection: Any = field(init=False, default=None)

    def __post_init__(self) -> None:
        ef = get_embedding_function(self.embedding_backend)

        if self.ephemeral:
            self._client = chromadb.EphemeralClient()
            # Always start with a clean collection in ephemeral mode
            try:
                self._client.delete_collection(COLLECTION_NAME)
            except Exception:
                pass
        else:
            self._client = chromadb.PersistentClient(path=self.persist_dir)

        self._collection = self._client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=ef,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(
            "VectorStore ready (%s, collection=%s, count=%d)",
            "ephemeral" if self.ephemeral else self.persist_dir,
            COLLECTION_NAME,
            self._collection.count(),
        )

    # ── CRUD ──────────────────────────────────────────────────────────────────

    def add(self, docs: List[Dict[str, Any]]) -> None:
        """
        Upsert a batch of documents.

        Each dict must have ``id`` (str) and ``document`` (str); optional
        ``metadata`` (dict).
        """
        if not docs:
            return
        ids = [d["id"] for d in docs]
        documents = [d["document"] for d in docs]
        metadatas = [d.get("metadata", {}) for d in docs]
        self._collection.upsert(ids=ids, documents=documents, metadatas=metadatas)

    def delete(self, ids: List[str]) -> None:
        """Delete documents by ID."""
        if ids:
            self._collection.delete(ids=ids)

    def count(self) -> int:
        """Return the number of documents in the collection."""
        return self._collection.count()

    # ── Search ────────────────────────────────────────────────────────────────

    def query(
        self,
        query_text: str,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """
        Semantic similarity search.

        Parameters
        ----------
        query_text:
            The user query string.
        n_results:
            Number of top results to return (capped at collection size).
        where:
            ChromaDB ``where`` filter dict, e.g. ``{"category": "policy"}``.
        """
        if self._collection.count() == 0:
            return []

        n = min(n_results, self._collection.count())

        if where:
            # ChromaDB raises an error when n_results exceeds the number of
            # documents that match the where filter.  Pre-fetch up to n IDs
            # to determine the actual filtered count and cap n accordingly.
            filtered = self._collection.get(where=where, limit=n, include=[])
            n = len(filtered["ids"])
            if n == 0:
                return []

        kwargs: Dict[str, Any] = {
            "query_texts": [query_text],
            "n_results": n,
            "include": ["documents", "metadatas", "distances"],
        }
        if where:
            kwargs["where"] = where

        raw = self._collection.query(**kwargs)

        results: List[SearchResult] = []
        for idx, doc_id in enumerate(raw["ids"][0]):
            results.append(
                SearchResult(
                    id=doc_id,
                    document=raw["documents"][0][idx],
                    metadata=raw["metadatas"][0][idx] or {},
                    distance=float(raw["distances"][0][idx]),
                )
            )
        return results

    def get_by_ids(self, ids: List[str]) -> List[SearchResult]:
        """Fetch documents by their IDs."""
        if not ids:
            return []
        raw = self._collection.get(ids=ids, include=["documents", "metadatas"])
        results = []
        for idx, doc_id in enumerate(raw["ids"]):
            results.append(
                SearchResult(
                    id=doc_id,
                    document=raw["documents"][idx],
                    metadata=raw["metadatas"][idx] or {},
                )
            )
        return results
