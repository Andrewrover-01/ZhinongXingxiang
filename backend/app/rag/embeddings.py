"""
Embedding function factory.

Supports three backends (in priority order):
1. ``openai``  — when OPENAI_API_KEY is set; best quality for Chinese text.
2. ``default`` — ChromaDB built-in (all-MiniLM-L6-v2 via onnxruntime);
                 ~90 MB one-time download, fully offline afterwards.
3. ``mock``    — deterministic pseudo-embeddings with no external deps;
                 used in unit tests via the CHROMA_EMBEDDING_BACKEND=mock setting.
"""

from __future__ import annotations

import hashlib
import random
from typing import List

from app.core.config import settings


# ── ChromaDB Embedding Function Protocol ──────────────────────────────────────

class _MockEmbeddingFunction:
    """
    Deterministic 384-dim pseudo-embeddings for testing.
    No model download required; embeddings are stable for the same text.
    """

    DIMENSION = 384

    def __call__(self, input: List[str]) -> List[List[float]]:  # noqa: A002
        result = []
        for text in input:
            seed = int(hashlib.md5(text.encode()).hexdigest(), 16) % (2**32)
            rng = random.Random(seed)
            vec = [rng.gauss(0, 1) for _ in range(self.DIMENSION)]
            magnitude = sum(x * x for x in vec) ** 0.5 or 1.0
            result.append([x / magnitude for x in vec])
        return result


def get_embedding_function(backend: str | None = None):
    """
    Return an embedding function compatible with the ChromaDB EF protocol.

    Parameters
    ----------
    backend:
        Override the backend. If *None*, the value from
        ``settings.CHROMA_EMBEDDING_BACKEND`` is used, defaulting to
        ``"default"`` when the setting is absent.
    """
    chosen = backend or getattr(settings, "CHROMA_EMBEDDING_BACKEND", "default")

    if chosen == "mock":
        return _MockEmbeddingFunction()

    if chosen == "openai" and settings.OPENAI_API_KEY:
        from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction  # type: ignore

        return OpenAIEmbeddingFunction(
            api_key=settings.OPENAI_API_KEY,
            model_name="text-embedding-3-small",
        )

    # Fall through to ChromaDB built-in (onnxruntime, ~90 MB download once)
    from chromadb.utils.embedding_functions import DefaultEmbeddingFunction  # type: ignore

    return DefaultEmbeddingFunction()
