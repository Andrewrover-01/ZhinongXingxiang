"""
Full RAG pipeline:
retrieve (hybrid) → build prompt context → generate answer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, AsyncGenerator, Dict, List, Optional

from app.rag.llm import LLMClient, get_llm_client
from app.rag.retriever import HybridRetriever
from app.rag.vector_store import SearchResult, VectorStore, get_vector_store


@dataclass
class RAGSource:
    id: str
    title: str
    category: str
    snippet: str  # first 200 chars of content
    distance: float


@dataclass
class RAGResult:
    answer: str
    sources: List[RAGSource] = field(default_factory=list)


def _to_rag_source(result: SearchResult) -> RAGSource:
    meta = result.metadata
    return RAGSource(
        id=result.id,
        title=meta.get("title", result.id),
        category=meta.get("category", ""),
        snippet=result.document[:200],
        distance=result.distance,
    )


def _result_to_dict(r: SearchResult) -> Dict[str, Any]:
    return {"document": r.document, "metadata": r.metadata}


class RAGChain:
    """
    Full RAG chain wiring together retrieval and generation.

    Parameters
    ----------
    vector_store:
        Injected for testability; defaults to the global singleton.
    llm_client:
        Injected for testability; defaults to the global singleton.
    n_semantic:
        Semantic candidate pool size fed to the hybrid retriever.
    n_results:
        Final number of documents used as LLM context.
    """

    def __init__(
        self,
        vector_store: Optional[VectorStore] = None,
        llm_client: Optional[LLMClient] = None,
        n_semantic: int = 20,
        n_results: int = 5,
    ) -> None:
        self._vs = vector_store or get_vector_store()
        self._llm = llm_client or get_llm_client()
        self._retriever = HybridRetriever(
            self._vs, n_semantic=n_semantic, n_results=n_results
        )

    # ── Non-streaming ─────────────────────────────────────────────────────────

    async def arun(
        self,
        query: str,
        category_filter: Optional[str] = None,
        system_prompt: Optional[str] = None,
    ) -> RAGResult:
        """Run the full RAG pipeline and return a complete answer."""
        where = {"category": category_filter} if category_filter else None
        candidates = self._retriever.retrieve(query, where=where)
        source_dicts = [_result_to_dict(r) for r in candidates]
        answer = await self._llm.complete(query, source_dicts, system_prompt)
        return RAGResult(
            answer=answer,
            sources=[_to_rag_source(r) for r in candidates],
        )

    # ── Streaming ─────────────────────────────────────────────────────────────

    async def astream(
        self,
        query: str,
        category_filter: Optional[str] = None,
        system_prompt: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """Yield answer chunks for SSE streaming."""
        where = {"category": category_filter} if category_filter else None
        candidates = self._retriever.retrieve(query, where=where)
        source_dicts = [_result_to_dict(r) for r in candidates]
        async for chunk in self._llm.stream(query, source_dicts, system_prompt):
            yield chunk


# Module-level singleton
_rag_chain: RAGChain | None = None


def get_rag_chain() -> RAGChain:
    global _rag_chain
    if _rag_chain is None:
        _rag_chain = RAGChain()
    return _rag_chain


def reset_rag_chain() -> None:
    """Reset the singleton (used in tests)."""
    global _rag_chain
    _rag_chain = None
