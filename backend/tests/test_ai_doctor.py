"""
tests/test_ai_doctor.py
AI 医生诊断 API 集成测试。

覆盖:
  POST /api/v1/ai-doctor/diagnose          非流式诊断
  POST /api/v1/ai-doctor/diagnose/stream   SSE 流式诊断
  GET  /api/v1/ai-doctor/records           历史记录列表
  GET  /api/v1/ai-doctor/records/{id}      单条历史记录
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.core.database import get_db
from app.main import app
from app.rag.chain import RAGChain, reset_rag_chain
from app.rag.llm import LLMClient
from app.rag.vector_store import VectorStore
from app.routers.deps import get_current_user


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture()
def ephemeral_vs() -> VectorStore:
    return VectorStore(ephemeral=True, embedding_backend="mock")


@pytest.fixture()
def mock_chain(ephemeral_vs: VectorStore) -> RAGChain:
    """RAGChain using ephemeral VS + no-key LLM (fallback mode)."""
    return RAGChain(vector_store=ephemeral_vs, llm_client=LLMClient(), n_results=3)


@pytest.fixture()
def client(db, mock_chain: RAGChain):
    from app.rag.chain import get_rag_chain

    def override_db():
        try:
            yield db
        finally:
            pass

    def override_chain():
        return mock_chain

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_rag_chain] = override_chain

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
    reset_rag_chain()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _register_and_login(client: TestClient, username: str, phone: str) -> str:
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


_DIAGNOSE_PAYLOAD = {
    "image_url": "https://example.com/rice_leaf.jpg",
    "description": "水稻叶片出现褐色斑点，边缘发黄",
    "crop_type": "水稻",
}


# ── Diagnose (non-streaming) tests ────────────────────────────────────────────

class TestDiagnose:
    def test_diagnose_success(self, client: TestClient):
        token = _register_and_login(client, "doctor_user1", "14000000001")
        resp = client.post(
            "/api/v1/ai-doctor/diagnose",
            json=_DIAGNOSE_PAYLOAD,
            headers=_auth(token),
        )
        assert resp.status_code == 201
        data = resp.json()
        assert "record_id" in data
        assert "diagnosis" in data
        assert "treatment_plan" in data
        assert "llm_model" in data
        assert isinstance(data["sources"], list)

    def test_diagnose_requires_auth(self, client: TestClient):
        resp = client.post("/api/v1/ai-doctor/diagnose", json=_DIAGNOSE_PAYLOAD)
        assert resp.status_code == 401

    def test_diagnose_missing_image_url(self, client: TestClient):
        token = _register_and_login(client, "doctor_user2", "14000000002")
        resp = client.post(
            "/api/v1/ai-doctor/diagnose",
            json={"description": "描述"},
            headers=_auth(token),
        )
        assert resp.status_code == 422

    def test_diagnose_with_minimal_payload(self, client: TestClient):
        token = _register_and_login(client, "doctor_user3", "14000000003")
        resp = client.post(
            "/api/v1/ai-doctor/diagnose",
            json={"image_url": "https://example.com/img.jpg"},
            headers=_auth(token),
        )
        assert resp.status_code == 201

    def test_diagnose_persists_record(self, client: TestClient):
        token = _register_and_login(client, "doctor_user4", "14000000004")
        client.post(
            "/api/v1/ai-doctor/diagnose",
            json=_DIAGNOSE_PAYLOAD,
            headers=_auth(token),
        )
        records_resp = client.get("/api/v1/ai-doctor/records", headers=_auth(token))
        assert records_resp.status_code == 200
        assert len(records_resp.json()) >= 1

    def test_diagnose_confidence_range(self, client: TestClient):
        token = _register_and_login(client, "doctor_user5", "14000000005")
        resp = client.post(
            "/api/v1/ai-doctor/diagnose",
            json=_DIAGNOSE_PAYLOAD,
            headers=_auth(token),
        )
        data = resp.json()
        if data.get("confidence") is not None:
            assert 0.0 <= data["confidence"] <= 1.0


# ── Streaming diagnose tests ──────────────────────────────────────────────────

class TestDiagnoseStream:
    def test_stream_returns_200(self, client: TestClient):
        token = _register_and_login(client, "stream_user1", "14100000001")
        resp = client.post(
            "/api/v1/ai-doctor/diagnose/stream",
            json=_DIAGNOSE_PAYLOAD,
            headers=_auth(token),
        )
        assert resp.status_code == 200

    def test_stream_requires_auth(self, client: TestClient):
        resp = client.post(
            "/api/v1/ai-doctor/diagnose/stream",
            json=_DIAGNOSE_PAYLOAD,
        )
        assert resp.status_code == 401

    def test_stream_contains_done_sentinel(self, client: TestClient):
        token = _register_and_login(client, "stream_user2", "14100000002")
        resp = client.post(
            "/api/v1/ai-doctor/diagnose/stream",
            json=_DIAGNOSE_PAYLOAD,
            headers=_auth(token),
        )
        assert resp.status_code == 200
        body = resp.text
        assert "[DONE]" in body

    def test_stream_content_type_sse(self, client: TestClient):
        token = _register_and_login(client, "stream_user3", "14100000003")
        resp = client.post(
            "/api/v1/ai-doctor/diagnose/stream",
            json=_DIAGNOSE_PAYLOAD,
            headers=_auth(token),
        )
        assert "text/event-stream" in resp.headers.get("content-type", "")

    def test_stream_missing_image_url(self, client: TestClient):
        token = _register_and_login(client, "stream_user4", "14100000004")
        resp = client.post(
            "/api/v1/ai-doctor/diagnose/stream",
            json={"description": "描述"},
            headers=_auth(token),
        )
        assert resp.status_code == 422


# ── Records tests ─────────────────────────────────────────────────────────────

class TestRecords:
    def test_list_records_empty(self, client: TestClient):
        token = _register_and_login(client, "records_user1", "14200000001")
        resp = client.get("/api/v1/ai-doctor/records", headers=_auth(token))
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_records_after_diagnose(self, client: TestClient):
        token = _register_and_login(client, "records_user2", "14200000002")
        client.post(
            "/api/v1/ai-doctor/diagnose",
            json=_DIAGNOSE_PAYLOAD,
            headers=_auth(token),
        )
        resp = client.get("/api/v1/ai-doctor/records", headers=_auth(token))
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_list_records_requires_auth(self, client: TestClient):
        resp = client.get("/api/v1/ai-doctor/records")
        assert resp.status_code == 401

    def test_get_single_record(self, client: TestClient):
        token = _register_and_login(client, "records_user3", "14200000003")
        diag_resp = client.post(
            "/api/v1/ai-doctor/diagnose",
            json=_DIAGNOSE_PAYLOAD,
            headers=_auth(token),
        )
        record_id = diag_resp.json()["record_id"]
        resp = client.get(f"/api/v1/ai-doctor/records/{record_id}", headers=_auth(token))
        assert resp.status_code == 200
        assert resp.json()["record_id"] == record_id

    def test_get_nonexistent_record(self, client: TestClient):
        token = _register_and_login(client, "records_user4", "14200000004")
        resp = client.get(
            "/api/v1/ai-doctor/records/nonexistent-uuid",
            headers=_auth(token),
        )
        assert resp.status_code == 404

    def test_records_isolated_between_users(self, client: TestClient):
        token_a = _register_and_login(client, "records_user5a", "14200000005")
        token_b = _register_and_login(client, "records_user5b", "14200000006")
        diag_resp = client.post(
            "/api/v1/ai-doctor/diagnose",
            json=_DIAGNOSE_PAYLOAD,
            headers=_auth(token_a),
        )
        record_id = diag_resp.json()["record_id"]
        # User B cannot access user A's record
        resp = client.get(f"/api/v1/ai-doctor/records/{record_id}", headers=_auth(token_b))
        assert resp.status_code == 404

    def test_record_schema(self, client: TestClient):
        token = _register_and_login(client, "records_user6", "14200000007")
        client.post(
            "/api/v1/ai-doctor/diagnose",
            json=_DIAGNOSE_PAYLOAD,
            headers=_auth(token),
        )
        records = client.get("/api/v1/ai-doctor/records", headers=_auth(token)).json()
        r = records[0]
        assert "record_id" in r
        assert "image_url" in r
        assert "diagnosis" in r
        assert "treatment_plan" in r
        assert "llm_model" in r
        assert "created_at" in r
