"""
app/core/cache.py

Async Redis cache helpers.

Design goals:
- Graceful degradation: if Redis is unavailable the application continues to
  work without caching (the caller just doesn't benefit from caching).
- Simple JSON-based serialization — only serialisable values are cached.
- A single module-level connection pool is shared across requests.
"""

from __future__ import annotations

import hashlib
import json
import logging
from typing import Any, Optional

import redis.asyncio as aioredis

from app.core.config import settings

logger = logging.getLogger(__name__)

# ── Connection pool ───────────────────────────────────────────────────────────

_pool: Optional[aioredis.ConnectionPool] = None


def _get_pool() -> aioredis.ConnectionPool:
    global _pool
    if _pool is None:
        _pool = aioredis.ConnectionPool.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            max_connections=20,
        )
    return _pool


def get_redis() -> aioredis.Redis:
    """Return an async Redis client backed by the shared connection pool."""
    return aioredis.Redis(connection_pool=_get_pool())


async def close_redis() -> None:
    """Close the connection pool (call on application shutdown)."""
    global _pool
    if _pool is not None:
        await _pool.aclose()
        _pool = None


# ── Public helpers ────────────────────────────────────────────────────────────

async def cache_get(key: str) -> Optional[Any]:
    """
    Retrieve a cached value by key.

    Returns the deserialised value, or *None* if the key does not exist or
    Redis is unavailable.
    """
    try:
        r = get_redis()
        raw = await r.get(key)
        if raw is None:
            return None
        return json.loads(raw)
    except Exception as exc:  # noqa: BLE001
        logger.warning("[cache] cache_get failed (key=%s): %s", key, exc)
        return None


async def cache_set(key: str, value: Any, ttl: Optional[int] = None) -> bool:
    """
    Store a JSON-serialisable *value* under *key*.

    Parameters
    ----------
    key:
        Redis key.
    value:
        Any JSON-serialisable object.
    ttl:
        Time-to-live in seconds.  Falls back to ``settings.CACHE_TTL`` (1 hr).

    Returns True on success, False if Redis is unavailable.
    """
    effective_ttl = ttl if ttl is not None else settings.CACHE_TTL
    try:
        r = get_redis()
        await r.set(key, json.dumps(value, ensure_ascii=False), ex=effective_ttl)
        return True
    except Exception as exc:  # noqa: BLE001
        logger.warning("[cache] cache_set failed (key=%s): %s", key, exc)
        return False


async def cache_delete(key: str) -> bool:
    """Delete a key. Returns True on success, False on error."""
    try:
        r = get_redis()
        await r.delete(key)
        return True
    except Exception as exc:  # noqa: BLE001
        logger.warning("[cache] cache_delete failed (key=%s): %s", key, exc)
        return False


async def cache_exists(key: str) -> bool:
    """Return True if key exists in Redis, False otherwise or on error."""
    try:
        r = get_redis()
        return bool(await r.exists(key))
    except Exception as exc:  # noqa: BLE001
        logger.warning("[cache] cache_exists failed (key=%s): %s", key, exc)
        return False


# ── Key builders ──────────────────────────────────────────────────────────────

def make_rag_cache_key(query: str, category: Optional[str] = None) -> str:
    """
    Build a stable cache key for a RAG query.

    Uses an MD5 digest of the query so the key stays compact regardless of
    query length.  Category is appended so diagnose and policy queries never
    collide.

    Example: ``rag:d41d8cd98f00b204e9800998ecf8427e:disease``
    """
    digest = hashlib.md5(query.encode("utf-8")).hexdigest()
    cat = category or "all"
    return f"rag:{digest}:{cat}"
