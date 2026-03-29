"""
tests/test_knowledge.py
知识库 API 集成测试 — CRUD + 语义搜索端点。

覆盖:
  GET    /api/v1/knowledge/           列表（分页、分类过滤）
  POST   /api/v1/knowledge/           创建（需认证）
  GET    /api/v1/knowledge/{id}       获取单条
  PUT    /api/v1/knowledge/{id}       更新（需认证）
  DELETE /api/v1/knowledge/{id}       删除（需认证）
  GET    /api/v1/knowledge/search     语义搜索
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.core.database import get_db
from app.main import app
from app.rag.vector_store import VectorStore


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture()
def ephemeral_vs() -> VectorStore:
    """Fresh in-memory VectorStore with mock embeddings for each test."""
    return VectorStore(ephemeral=True, embedding_backend="mock")


@pytest.fixture()
def client(db, ephemeral_vs: VectorStore):
    """
    TestClient with:
    - SQLite test DB (via `db` fixture from conftest)
    - Ephemeral VectorStore (no disk I/O, no ChromaDB persistence)
    """
    from app.routers.knowledge import _vs

    def override_get_db():
        try:
            yield db
        finally:
            pass

    def override_vs():
        return ephemeral_vs

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[_vs] = override_vs

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _register_and_login(client: TestClient, username: str, phone: str) -> str:
    """Register a user and return a Bearer token."""
    client.post(
        "/api/v1/auth/register",
        json={"username": username, "phone": phone, "password": "testpass"},
    )
    resp = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": "testpass"},
    )
    return resp.json()["access_token"]


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


_SAMPLE_DOC = {
    "title": "水稻稻瘟病综合防治技术",
    "category": "disease",
    "content": "水稻稻瘟病是水稻生产中最重要的病害之一，主要防治措施包括：选用抗病品种、合理施肥、及时喷施三环唑等。",
    "crop_types": "水稻",
    "is_verified": True,
}


# ── List tests ────────────────────────────────────────────────────────────────

class TestListKnowledge:
    def test_list_empty(self, client: TestClient):
        resp = client.get("/api/v1/knowledge/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0
        assert data["items"] == []

    def test_list_after_create(self, client: TestClient):
        token = _register_and_login(client, "list_user1", "13000000001")
        client.post("/api/v1/knowledge/", json=_SAMPLE_DOC, headers=_auth(token))
        resp = client.get("/api/v1/knowledge/")
        assert resp.status_code == 200
        assert resp.json()["total"] == 1

    def test_list_pagination_limit(self, client: TestClient):
        token = _register_and_login(client, "list_user2", "13000000002")
        for i in range(5):
            doc = {**_SAMPLE_DOC, "title": f"文档{i}"}
            client.post("/api/v1/knowledge/", json=doc, headers=_auth(token))
        resp = client.get("/api/v1/knowledge/?limit=2")
        assert resp.status_code == 200
        assert len(resp.json()["items"]) == 2

    def test_list_pagination_skip(self, client: TestClient):
        token = _register_and_login(client, "list_user3", "13000000003")
        for i in range(3):
            client.post(
                "/api/v1/knowledge/",
                json={**_SAMPLE_DOC, "title": f"分页文档{i}"},
                headers=_auth(token),
            )
        resp = client.get("/api/v1/knowledge/?skip=2&limit=10")
        assert resp.status_code == 200
        assert resp.json()["total"] == 3
        assert len(resp.json()["items"]) == 1

    def test_list_category_filter(self, client: TestClient):
        token = _register_and_login(client, "list_user4", "13000000004")
        client.post("/api/v1/knowledge/", json={**_SAMPLE_DOC, "category": "disease"}, headers=_auth(token))
        client.post("/api/v1/knowledge/", json={**_SAMPLE_DOC, "title": "政策文档", "category": "policy"}, headers=_auth(token))
        resp = client.get("/api/v1/knowledge/?category=disease")
        assert resp.status_code == 200
        for item in resp.json()["items"]:
            assert item["category"] == "disease"

    def test_list_no_auth_required(self, client: TestClient):
        """GET /knowledge/ is public — no token needed."""
        resp = client.get("/api/v1/knowledge/")
        assert resp.status_code == 200


# ── Create tests ──────────────────────────────────────────────────────────────

class TestCreateKnowledge:
    def test_create_success(self, client: TestClient):
        token = _register_and_login(client, "create_user1", "13100000001")
        resp = client.post("/api/v1/knowledge/", json=_SAMPLE_DOC, headers=_auth(token))
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == _SAMPLE_DOC["title"]
        assert data["category"] == _SAMPLE_DOC["category"]
        assert data["content"] == _SAMPLE_DOC["content"]
        assert "id" in data
        assert "created_at" in data

    def test_create_requires_auth(self, client: TestClient):
        resp = client.post("/api/v1/knowledge/", json=_SAMPLE_DOC)
        assert resp.status_code == 401

    def test_create_invalid_token(self, client: TestClient):
        resp = client.post(
            "/api/v1/knowledge/",
            json=_SAMPLE_DOC,
            headers={"Authorization": "Bearer invalid"},
        )
        assert resp.status_code == 401

    def test_create_missing_required_fields(self, client: TestClient):
        token = _register_and_login(client, "create_user2", "13100000002")
        resp = client.post(
            "/api/v1/knowledge/",
            json={"title": "缺少字段"},  # missing category and content
            headers=_auth(token),
        )
        assert resp.status_code == 422

    def test_create_optional_fields_default(self, client: TestClient):
        token = _register_and_login(client, "create_user3", "13100000003")
        minimal = {"title": "最简文档", "category": "technique", "content": "内容正文"}
        resp = client.post("/api/v1/knowledge/", json=minimal, headers=_auth(token))
        assert resp.status_code == 201
        data = resp.json()
        assert data["is_verified"] is False
        assert data["source"] is None

    def test_create_syncs_to_vector_store(self, client: TestClient, ephemeral_vs: VectorStore):
        token = _register_and_login(client, "create_user4", "13100000004")
        client.post("/api/v1/knowledge/", json=_SAMPLE_DOC, headers=_auth(token))
        assert ephemeral_vs.count() == 1


# ── Get single document tests ─────────────────────────────────────────────────

class TestGetKnowledge:
    def test_get_existing_doc(self, client: TestClient):
        token = _register_and_login(client, "get_user1", "13200000001")
        create_resp = client.post("/api/v1/knowledge/", json=_SAMPLE_DOC, headers=_auth(token))
        doc_id = create_resp.json()["id"]

        resp = client.get(f"/api/v1/knowledge/{doc_id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == doc_id
        assert resp.json()["title"] == _SAMPLE_DOC["title"]

    def test_get_nonexistent_returns_404(self, client: TestClient):
        resp = client.get("/api/v1/knowledge/nonexistent-uuid-1234")
        assert resp.status_code == 404

    def test_get_no_auth_required(self, client: TestClient):
        """GET by ID is public."""
        token = _register_and_login(client, "get_user2", "13200000002")
        create_resp = client.post("/api/v1/knowledge/", json=_SAMPLE_DOC, headers=_auth(token))
        doc_id = create_resp.json()["id"]
        resp = client.get(f"/api/v1/knowledge/{doc_id}")
        assert resp.status_code == 200


# ── Update tests ──────────────────────────────────────────────────────────────

class TestUpdateKnowledge:
    def test_update_title(self, client: TestClient):
        token = _register_and_login(client, "update_user1", "13300000001")
        create_resp = client.post("/api/v1/knowledge/", json=_SAMPLE_DOC, headers=_auth(token))
        doc_id = create_resp.json()["id"]

        resp = client.put(
            f"/api/v1/knowledge/{doc_id}",
            json={"title": "更新后的标题"},
            headers=_auth(token),
        )
        assert resp.status_code == 200
        assert resp.json()["title"] == "更新后的标题"

    def test_update_content_resyncs_vector_store(self, client: TestClient, ephemeral_vs: VectorStore):
        token = _register_and_login(client, "update_user2", "13300000002")
        create_resp = client.post("/api/v1/knowledge/", json=_SAMPLE_DOC, headers=_auth(token))
        doc_id = create_resp.json()["id"]
        count_before = ephemeral_vs.count()

        client.put(
            f"/api/v1/knowledge/{doc_id}",
            json={"content": "更新后的内容，重新入向量库。"},
            headers=_auth(token),
        )
        # Upsert keeps count the same
        assert ephemeral_vs.count() == count_before

    def test_update_requires_auth(self, client: TestClient):
        token = _register_and_login(client, "update_user3", "13300000003")
        create_resp = client.post("/api/v1/knowledge/", json=_SAMPLE_DOC, headers=_auth(token))
        doc_id = create_resp.json()["id"]

        resp = client.put(f"/api/v1/knowledge/{doc_id}", json={"title": "未授权更新"})
        assert resp.status_code == 401

    def test_update_nonexistent_returns_404(self, client: TestClient):
        token = _register_and_login(client, "update_user4", "13300000004")
        resp = client.put(
            "/api/v1/knowledge/nonexistent-uuid-9999",
            json={"title": "不存在"},
            headers=_auth(token),
        )
        assert resp.status_code == 404


# ── Delete tests ──────────────────────────────────────────────────────────────

class TestDeleteKnowledge:
    def test_delete_success(self, client: TestClient):
        token = _register_and_login(client, "delete_user1", "13400000001")
        create_resp = client.post("/api/v1/knowledge/", json=_SAMPLE_DOC, headers=_auth(token))
        doc_id = create_resp.json()["id"]

        resp = client.delete(f"/api/v1/knowledge/{doc_id}", headers=_auth(token))
        assert resp.status_code == 204

        # Verify gone
        assert client.get(f"/api/v1/knowledge/{doc_id}").status_code == 404

    def test_delete_removes_from_vector_store(self, client: TestClient, ephemeral_vs: VectorStore):
        token = _register_and_login(client, "delete_user2", "13400000002")
        create_resp = client.post("/api/v1/knowledge/", json=_SAMPLE_DOC, headers=_auth(token))
        doc_id = create_resp.json()["id"]
        assert ephemeral_vs.count() == 1

        client.delete(f"/api/v1/knowledge/{doc_id}", headers=_auth(token))
        assert ephemeral_vs.count() == 0

    def test_delete_requires_auth(self, client: TestClient):
        token = _register_and_login(client, "delete_user3", "13400000003")
        create_resp = client.post("/api/v1/knowledge/", json=_SAMPLE_DOC, headers=_auth(token))
        doc_id = create_resp.json()["id"]

        resp = client.delete(f"/api/v1/knowledge/{doc_id}")
        assert resp.status_code == 401

    def test_delete_nonexistent_returns_404(self, client: TestClient):
        token = _register_and_login(client, "delete_user4", "13400000004")
        resp = client.delete(
            "/api/v1/knowledge/nonexistent-uuid-0000",
            headers=_auth(token),
        )
        assert resp.status_code == 404


# ── Search tests ──────────────────────────────────────────────────────────────

class TestSearchKnowledge:
    def test_search_returns_list(self, client: TestClient):
        resp = client.get("/api/v1/knowledge/search?q=水稻病害")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_search_returns_results_after_ingest(self, client: TestClient):
        token = _register_and_login(client, "search_user1", "13500000001")
        client.post("/api/v1/knowledge/", json=_SAMPLE_DOC, headers=_auth(token))

        resp = client.get("/api/v1/knowledge/search?q=水稻稻瘟病")
        assert resp.status_code == 200
        results = resp.json()
        assert len(results) >= 1

    def test_search_result_schema(self, client: TestClient):
        token = _register_and_login(client, "search_user2", "13500000002")
        client.post("/api/v1/knowledge/", json=_SAMPLE_DOC, headers=_auth(token))

        resp = client.get("/api/v1/knowledge/search?q=稻瘟病防治")
        assert resp.status_code == 200
        for item in resp.json():
            assert "id" in item
            assert "title" in item
            assert "category" in item
            assert "snippet" in item
            assert "similarity" in item
            assert isinstance(item["similarity"], float)

    def test_search_with_category_filter(self, client: TestClient):
        token = _register_and_login(client, "search_user3", "13500000003")
        client.post("/api/v1/knowledge/", json={**_SAMPLE_DOC, "category": "disease"}, headers=_auth(token))
        client.post(
            "/api/v1/knowledge/",
            json={**_SAMPLE_DOC, "title": "补贴政策", "category": "policy", "content": "粮食补贴政策"},
            headers=_auth(token),
        )

        resp = client.get("/api/v1/knowledge/search?q=防治&category=disease")
        assert resp.status_code == 200
        for item in resp.json():
            assert item["category"] == "disease"

    def test_search_requires_query_param(self, client: TestClient):
        resp = client.get("/api/v1/knowledge/search")
        assert resp.status_code == 422

    def test_search_empty_query_rejected(self, client: TestClient):
        resp = client.get("/api/v1/knowledge/search?q=")
        assert resp.status_code == 422

    def test_search_n_parameter(self, client: TestClient):
        token = _register_and_login(client, "search_user4", "13500000004")
        for i in range(5):
            client.post(
                "/api/v1/knowledge/",
                json={**_SAMPLE_DOC, "title": f"搜索文档{i}"},
                headers=_auth(token),
            )
        resp = client.get("/api/v1/knowledge/search?q=水稻&n=2")
        assert resp.status_code == 200
        assert len(resp.json()) <= 2

    def test_search_no_auth_required(self, client: TestClient):
        """Search endpoint is public."""
        resp = client.get("/api/v1/knowledge/search?q=水稻")
        assert resp.status_code == 200
