"""
tests/test_rag.py
RAG 引擎单元测试 — VectorStore、HybridRetriever、RAGChain。

所有测试使用 ephemeral（内存）VectorStore + mock embedding，
无需持久化磁盘或外部服务。
"""

from __future__ import annotations

import asyncio
import pytest

from app.rag.vector_store import VectorStore, SearchResult, reset_vector_store


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture()
def vs() -> VectorStore:
    """Ephemeral VectorStore with deterministic mock embeddings."""
    return VectorStore(ephemeral=True, embedding_backend="mock")


@pytest.fixture()
def populated_vs(vs: VectorStore) -> VectorStore:
    """VectorStore pre-loaded with 5 agriculture documents."""
    docs = [
        {
            "id": "doc1",
            "document": "水稻稻瘟病防治：喷施三环唑，保持田间通风透光，及时排水降湿。",
            "metadata": {"title": "水稻稻瘟病防治技术", "category": "disease", "crop_types": "水稻"},
        },
        {
            "id": "doc2",
            "document": "小麦白粉病防治：增施磷钾肥，喷施三唑酮，合理密植。",
            "metadata": {"title": "小麦白粉病防治", "category": "disease", "crop_types": "小麦"},
        },
        {
            "id": "doc3",
            "document": "玉米螟防治：释放赤眼蜂，灯光诱杀，喷施氯虫苯甲酰胺。",
            "metadata": {"title": "玉米螟防治指南", "category": "pest", "crop_types": "玉米"},
        },
        {
            "id": "doc4",
            "document": "耕地保护补贴：国家对种粮农民给予粮食直补，保障粮食安全。",
            "metadata": {"title": "耕地保护补贴政策", "category": "policy", "crop_types": ""},
        },
        {
            "id": "doc5",
            "document": "合理密植技术：根据品种特性确定播种量，保证植株充分受光。",
            "metadata": {"title": "合理密植技术要点", "category": "technique", "crop_types": "水稻"},
        },
    ]
    vs.add(docs)
    return vs


# ── VectorStore tests ─────────────────────────────────────────────────────────

class TestVectorStore:
    def test_initial_count_is_zero(self, vs: VectorStore):
        assert vs.count() == 0

    def test_add_increases_count(self, vs: VectorStore):
        vs.add([{"id": "a", "document": "水稻病害防治", "metadata": {"type": "test"}}])
        assert vs.count() == 1

    def test_add_multiple_docs(self, vs: VectorStore):
        docs = [{"id": f"d{i}", "document": f"文档内容{i}", "metadata": {"idx": str(i)}} for i in range(5)]
        vs.add(docs)
        assert vs.count() == 5

    def test_add_empty_is_noop(self, vs: VectorStore):
        vs.add([])
        assert vs.count() == 0

    def test_upsert_does_not_duplicate(self, vs: VectorStore):
        doc = {"id": "x1", "document": "原始内容", "metadata": {"v": "1"}}
        vs.add([doc])
        vs.add([{"id": "x1", "document": "更新内容", "metadata": {"v": "2"}}])
        assert vs.count() == 1

    def test_delete_removes_doc(self, populated_vs: VectorStore):
        before = populated_vs.count()
        populated_vs.delete(["doc1"])
        assert populated_vs.count() == before - 1

    def test_delete_nonexistent_is_safe(self, vs: VectorStore):
        vs.delete(["nonexistent_id"])  # should not raise
        assert vs.count() == 0

    def test_delete_empty_list_is_safe(self, vs: VectorStore):
        vs.delete([])  # should not raise

    def test_query_returns_results(self, populated_vs: VectorStore):
        results = populated_vs.query("稻瘟病防治方法", n_results=3)
        assert isinstance(results, list)
        assert len(results) >= 1
        assert all(isinstance(r, SearchResult) for r in results)

    def test_query_respects_n_results(self, populated_vs: VectorStore):
        results = populated_vs.query("农业技术", n_results=2)
        assert len(results) <= 2

    def test_query_result_has_required_fields(self, populated_vs: VectorStore):
        results = populated_vs.query("水稻病害", n_results=1)
        r = results[0]
        assert isinstance(r.id, str)
        assert isinstance(r.document, str)
        assert isinstance(r.metadata, dict)
        assert isinstance(r.distance, float)

    def test_query_with_where_filter(self, populated_vs: VectorStore):
        results = populated_vs.query("防治", n_results=5, where={"category": "disease"})
        for r in results:
            assert r.metadata.get("category") == "disease"

    def test_query_where_filter_n_results_exceeds_filtered_count(self, populated_vs: VectorStore):
        # populated_vs has only 1 "policy" document (doc4), but n_results=20.
        # ChromaDB would raise an error if we don't cap n_results to filtered count.
        results = populated_vs.query("补贴政策", n_results=20, where={"category": "policy"})
        assert isinstance(results, list)
        assert len(results) == 1
        assert results[0].metadata.get("category") == "policy"

    def test_query_where_filter_no_match_returns_empty(self, populated_vs: VectorStore):
        # No documents have category "weather" in the fixture.
        results = populated_vs.query("天气预报", n_results=5, where={"category": "weather"})
        assert results == []

    def test_query_empty_store_returns_empty(self, vs: VectorStore):
        results = vs.query("任意查询", n_results=5)
        assert results == []

    def test_get_by_ids_returns_docs(self, populated_vs: VectorStore):
        results = populated_vs.get_by_ids(["doc1", "doc3"])
        assert len(results) == 2
        ids = {r.id for r in results}
        assert "doc1" in ids
        assert "doc3" in ids

    def test_get_by_ids_empty_list(self, vs: VectorStore):
        results = vs.get_by_ids([])
        assert results == []


# ── HybridRetriever tests ─────────────────────────────────────────────────────

class TestHybridRetriever:
    def test_retrieve_returns_results(self, populated_vs: VectorStore):
        from app.rag.retriever import HybridRetriever
        retriever = HybridRetriever(populated_vs, n_semantic=5, n_results=3)
        results = retriever.retrieve("水稻稻瘟病怎么防治")
        assert len(results) >= 1

    def test_retrieve_respects_n_results(self, populated_vs: VectorStore):
        from app.rag.retriever import HybridRetriever
        retriever = HybridRetriever(populated_vs, n_semantic=5, n_results=2)
        results = retriever.retrieve("农业技术")
        assert len(results) <= 2

    def test_retrieve_empty_store_returns_empty(self, vs: VectorStore):
        from app.rag.retriever import HybridRetriever
        retriever = HybridRetriever(vs, n_semantic=5, n_results=3)
        results = retriever.retrieve("稻瘟病")
        assert results == []

    def test_retrieve_with_category_filter(self, populated_vs: VectorStore):
        from app.rag.retriever import HybridRetriever
        retriever = HybridRetriever(populated_vs, n_semantic=5, n_results=3)
        results = retriever.retrieve("防治", where={"category": "pest"})
        for r in results:
            assert r.metadata.get("category") == "pest"

    def test_retrieve_returns_search_results(self, populated_vs: VectorStore):
        from app.rag.retriever import HybridRetriever
        retriever = HybridRetriever(populated_vs, n_semantic=5, n_results=3)
        results = retriever.retrieve("小麦白粉病")
        assert all(isinstance(r, SearchResult) for r in results)


# ── RAGChain tests ────────────────────────────────────────────────────────────

class TestRAGChain:
    """RAGChain tests run without an OpenAI API key → fallback mode."""

    def test_arun_returns_rag_result(self, populated_vs: VectorStore):
        from app.rag.chain import RAGChain
        from app.rag.llm import LLMClient

        chain = RAGChain(vector_store=populated_vs, llm_client=LLMClient(), n_results=3)
        result = asyncio.get_event_loop().run_until_complete(
            chain.arun("水稻稻瘟病如何防治")
        )
        assert result.answer
        assert isinstance(result.sources, list)

    def test_arun_answer_is_string(self, populated_vs: VectorStore):
        from app.rag.chain import RAGChain
        from app.rag.llm import LLMClient

        chain = RAGChain(vector_store=populated_vs, llm_client=LLMClient(), n_results=3)
        result = asyncio.get_event_loop().run_until_complete(
            chain.arun("玉米螟虫害防治方法")
        )
        assert isinstance(result.answer, str)
        assert len(result.answer) > 0

    def test_arun_with_category_filter(self, populated_vs: VectorStore):
        from app.rag.chain import RAGChain
        from app.rag.llm import LLMClient

        chain = RAGChain(vector_store=populated_vs, llm_client=LLMClient(), n_results=3)
        result = asyncio.get_event_loop().run_until_complete(
            chain.arun("补贴政策", category_filter="policy")
        )
        assert isinstance(result.answer, str)

    def test_arun_no_results_fallback(self, vs: VectorStore):
        from app.rag.chain import RAGChain
        from app.rag.llm import LLMClient

        chain = RAGChain(vector_store=vs, llm_client=LLMClient(), n_results=3)
        result = asyncio.get_event_loop().run_until_complete(
            chain.arun("不存在的查询内容xyz")
        )
        # Fallback answer should still return a string (no sources found message)
        assert isinstance(result.answer, str)

    def test_astream_yields_chunks(self, populated_vs: VectorStore):
        from app.rag.chain import RAGChain
        from app.rag.llm import LLMClient

        chain = RAGChain(vector_store=populated_vs, llm_client=LLMClient(), n_results=3)

        async def collect_chunks() -> list[str]:
            chunks = []
            async for chunk in chain.astream("水稻病害防治"):
                chunks.append(chunk)
            return chunks

        chunks = asyncio.get_event_loop().run_until_complete(collect_chunks())
        assert len(chunks) > 0
        full_text = "".join(chunks)
        assert len(full_text) > 0

    def test_rag_source_fields(self, populated_vs: VectorStore):
        from app.rag.chain import RAGChain, RAGSource
        from app.rag.llm import LLMClient

        chain = RAGChain(vector_store=populated_vs, llm_client=LLMClient(), n_results=3)
        result = asyncio.get_event_loop().run_until_complete(
            chain.arun("水稻稻瘟病")
        )
        for src in result.sources:
            assert isinstance(src, RAGSource)
            assert isinstance(src.id, str)
            assert isinstance(src.title, str)
            assert isinstance(src.snippet, str)
            assert len(src.snippet) <= 200

    def test_reset_vector_store_singleton(self):
        """reset_vector_store() clears the module-level singleton."""
        reset_vector_store()
        from app.rag.vector_store import _vector_store
        assert _vector_store is None
