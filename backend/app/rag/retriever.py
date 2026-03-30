"""
Hybrid retriever: vector (semantic) search + BM25 keyword search.

Flow
────
1. Semantic search via ChromaDB (top ``n_semantic`` results).
2. BM25 over the *semantic candidates* to re-score keyword relevance.
3. Reciprocal Rank Fusion (RRF) to merge both ranked lists.
4. Return top ``n_results`` de-duplicated documents.

Keeping BM25 scoped to the semantic candidates avoids O(N) traversal
of the entire corpus at query time.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional

from rank_bm25 import BM25Okapi  # type: ignore

from app.rag.vector_store import SearchResult, VectorStore


def _tokenize(text: str) -> List[str]:
    """Simple character-level n-gram + space tokenizer suitable for Chinese."""
    tokens: List[str] = []
    # Space-split for any Latin/numeric tokens
    for word in text.split():
        if len(word) == 1:
            tokens.append(word)
        else:
            # Bigram sliding window for CJK
            tokens.extend(word[i : i + 2] for i in range(len(word) - 1))
            tokens.append(word)
    return tokens or list(text)


def _rrf_score(rank: int, k: int = 60) -> float:
    """Reciprocal Rank Fusion score."""
    return 1.0 / (k + rank + 1)


class HybridRetriever:
    """
    Retrieve and re-rank documents using semantic search and BM25.

    Parameters
    ----------
    vector_store:
        The ``VectorStore`` instance to query.
    n_semantic:
        Number of candidates fetched from semantic search.
    n_results:
        Final number of documents returned after hybrid fusion.
    """

    def __init__(
        self,
        vector_store: VectorStore,
        n_semantic: int = 20,
        n_results: int = 5,
    ) -> None:
        self.vs = vector_store
        self.n_semantic = n_semantic
        self.n_results = n_results

    def retrieve(
        self,
        query: str,
        where: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """
        Run hybrid retrieval and return the top ``n_results`` documents.
        """
        # 1. Semantic candidates
        candidates = self.vs.query(query, n_results=self.n_semantic, where=where)
        if not candidates:
            return []

        # 2. BM25 over candidates
        corpus_tokens = [_tokenize(c.document) for c in candidates]
        bm25 = BM25Okapi(corpus_tokens)
        query_tokens = _tokenize(query)
        bm25_scores = bm25.get_scores(query_tokens)

        # 3. RRF fusion
        # Semantic rank is already ordered by distance (lower = better)
        sem_rank = {c.id: i for i, c in enumerate(candidates)}
        # BM25 rank: sort descending by score
        bm25_rank = {
            candidates[i].id: rank
            for rank, i in enumerate(
                sorted(range(len(candidates)), key=lambda x: -bm25_scores[x])
            )
        }

        fused: Dict[str, float] = {}
        for doc in candidates:
            fused[doc.id] = _rrf_score(sem_rank[doc.id]) + _rrf_score(
                bm25_rank[doc.id]
            )

        top_ids = sorted(fused, key=lambda x: -fused[x])[: self.n_results]
        id_to_doc = {c.id: c for c in candidates}
        return [id_to_doc[doc_id] for doc_id in top_ids if doc_id in id_to_doc]
