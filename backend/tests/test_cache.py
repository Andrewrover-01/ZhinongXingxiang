"""
tests/test_cache.py

Unit tests for the Redis cache layer (app/core/cache.py) and the
RAGChain cache integration (app/rag/chain.py).

Uses ``fakeredis`` so no real Redis server is needed.
"""

from __future__ import annotations

import asyncio
import pytest

import fakeredis.aioredis as fakeredis_async
import redis.asyncio as aioredis

from app.core import cache as cache_module
from app.core.cache import (
    cache_delete,
    cache_exists,
    cache_get,
    cache_set,
    make_rag_cache_key,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_fake_redis() -> aioredis.Redis:
    """Return a fakeredis client for isolation."""
    return fakeredis_async.FakeRedis(decode_responses=True)


@pytest.fixture(autouse=True)
def patch_redis(monkeypatch):
    """
    Replace the real Redis client returned by ``get_redis()`` with a
    fakeredis instance that resets between tests.
    """
    fake = _make_fake_redis()

    def _get_fake_redis():
        return fake

    monkeypatch.setattr(cache_module, "get_redis", _get_fake_redis)
    yield fake
    # Clean up (fakeredis is in-memory; the object is GC'd after yield)


# ── cache_set / cache_get ─────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_set_and_get_string():
    ok = await cache_set("key1", "hello")
    assert ok is True
    value = await cache_get("key1")
    assert value == "hello"


@pytest.mark.asyncio
async def test_set_and_get_dict():
    data = {"answer": "某种病害", "sources": [{"id": "doc1", "title": "水稻稻瘟病"}]}
    await cache_set("key2", data)
    result = await cache_get("key2")
    assert result == data


@pytest.mark.asyncio
async def test_get_missing_key_returns_none():
    result = await cache_get("nonexistent_key")
    assert result is None


@pytest.mark.asyncio
async def test_set_respects_ttl(monkeypatch):
    """
    Verify that a key with TTL=1 is set correctly (fakeredis supports TTL).
    The actual expiry isn't tested here because it would require sleeping —
    instead we confirm the key exists immediately after set.
    """
    await cache_set("ttl_key", {"x": 1}, ttl=1)
    assert await cache_get("ttl_key") == {"x": 1}


# ── cache_delete ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_delete_removes_key():
    await cache_set("del_key", 42)
    await cache_delete("del_key")
    assert await cache_get("del_key") is None


@pytest.mark.asyncio
async def test_delete_nonexistent_key_does_not_raise():
    result = await cache_delete("ghost_key")
    assert result is True


# ── cache_exists ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_exists_true_and_false():
    await cache_set("exists_key", "value")
    assert await cache_exists("exists_key") is True
    assert await cache_exists("missing_key") is False


# ── make_rag_cache_key ────────────────────────────────────────────────────────

def test_make_rag_cache_key_format():
    key = make_rag_cache_key("水稻稻瘟病防治", "disease")
    assert key.startswith("rag:")
    parts = key.split(":")
    assert len(parts) == 3
    assert parts[2] == "disease"


def test_make_rag_cache_key_no_category():
    key = make_rag_cache_key("测试查询")
    assert key.endswith(":all")


def test_make_rag_cache_key_same_query_same_key():
    k1 = make_rag_cache_key("same query", "policy")
    k2 = make_rag_cache_key("same query", "policy")
    assert k1 == k2


def test_make_rag_cache_key_different_query_different_key():
    k1 = make_rag_cache_key("query A", "disease")
    k2 = make_rag_cache_key("query B", "disease")
    assert k1 != k2


def test_make_rag_cache_key_different_category_different_key():
    k1 = make_rag_cache_key("same", "disease")
    k2 = make_rag_cache_key("same", "policy")
    assert k1 != k2


# ── RAGChain cache integration ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_rag_chain_caches_result(monkeypatch):
    """arun() result is stored in cache; second call returns cached value."""
    from app.rag.chain import RAGChain, reset_rag_chain
    from app.rag.vector_store import VectorStore
    from app.rag.llm import LLMClient

    reset_rag_chain()

    call_count = 0

    class _CountingLLM(LLMClient):
        async def complete(self, query, sources, system_prompt=None):
            nonlocal call_count
            call_count += 1
            return "诊断结果：水稻稻瘟病"

    vs = VectorStore(ephemeral=True, embedding_backend="mock")
    chain = RAGChain(
        vector_store=vs,
        llm_client=_CountingLLM(),
        enable_cache=True,
    )

    result1 = await chain.arun("水稻症状", category_filter="disease")
    assert call_count == 1
    assert "水稻稻瘟病" in result1.answer

    result2 = await chain.arun("水稻症状", category_filter="disease")
    assert call_count == 1  # LLM not called again — served from cache
    assert result2.answer == result1.answer


@pytest.mark.asyncio
async def test_rag_chain_cache_disabled(monkeypatch):
    """When enable_cache=False, every arun() call hits the LLM."""
    from app.rag.chain import RAGChain, reset_rag_chain
    from app.rag.vector_store import VectorStore
    from app.rag.llm import LLMClient

    reset_rag_chain()

    call_count = 0

    class _CountingLLM(LLMClient):
        async def complete(self, query, sources, system_prompt=None):
            nonlocal call_count
            call_count += 1
            return "答案"

    vs = VectorStore(ephemeral=True, embedding_backend="mock")
    chain = RAGChain(
        vector_store=vs,
        llm_client=_CountingLLM(),
        enable_cache=False,
    )

    await chain.arun("测试查询", category_filter="disease")
    await chain.arun("测试查询", category_filter="disease")
    assert call_count == 2  # cache disabled → both calls reach LLM


@pytest.mark.asyncio
async def test_rag_chain_cache_miss_then_hit_different_categories(monkeypatch):
    """Different category_filter values produce separate cache entries."""
    from app.rag.chain import RAGChain, reset_rag_chain
    from app.rag.vector_store import VectorStore
    from app.rag.llm import LLMClient

    reset_rag_chain()

    answers = {"disease": "病害答案", "policy": "政策答案"}
    call_log = []

    class _CategLLM(LLMClient):
        async def complete(self, query, sources, system_prompt=None):
            # Return a different answer per call order so we can detect
            # if the cache is being bypassed
            answer = f"答案{len(call_log)}"
            call_log.append(query)
            return answer

    vs = VectorStore(ephemeral=True, embedding_backend="mock")
    chain = RAGChain(
        vector_store=vs,
        llm_client=_CategLLM(),
        enable_cache=True,
    )

    r_disease1 = await chain.arun("测试", category_filter="disease")
    r_policy1 = await chain.arun("测试", category_filter="policy")
    r_disease2 = await chain.arun("测试", category_filter="disease")
    r_policy2 = await chain.arun("测试", category_filter="policy")

    # LLM should only be called twice (one per unique category)
    assert len(call_log) == 2
    assert r_disease1.answer == r_disease2.answer
    assert r_policy1.answer == r_policy2.answer
