"""
tests/test_policy.py
农业政策助手流式问答 API 集成测试。

覆盖:
  POST   /api/v1/policy/chat                  SSE 流式问答
  GET    /api/v1/policy/sessions              会话列表
  GET    /api/v1/policy/sessions/{session_id} 会话消息
  DELETE /api/v1/policy/sessions/{session_id} 删除会话
"""

from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient

from app.core.database import get_db
from app.main import app
from app.rag.chain import RAGChain, reset_rag_chain
from app.rag.llm import LLMClient
from app.rag.vector_store import VectorStore


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture()
def mock_chain() -> RAGChain:
    vs = VectorStore(ephemeral=True, embedding_backend="mock")
    return RAGChain(vector_store=vs, llm_client=LLMClient(), n_results=3)


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


def _new_session_id() -> str:
    return str(uuid.uuid4())


# ── Chat (SSE streaming) tests ────────────────────────────────────────────────

class TestPolicyChat:
    def test_chat_returns_200(self, client: TestClient):
        token = _register_and_login(client, "policy_user1", "15000000001")
        resp = client.post(
            "/api/v1/policy/chat",
            json={"session_id": _new_session_id(), "message": "种粮补贴政策有哪些？"},
            headers=_auth(token),
        )
        assert resp.status_code == 200

    def test_chat_content_type_sse(self, client: TestClient):
        token = _register_and_login(client, "policy_user2", "15000000002")
        resp = client.post(
            "/api/v1/policy/chat",
            json={"session_id": _new_session_id(), "message": "耕地保护补贴"},
            headers=_auth(token),
        )
        assert "text/event-stream" in resp.headers.get("content-type", "")

    def test_chat_contains_done_sentinel(self, client: TestClient):
        token = _register_and_login(client, "policy_user3", "15000000003")
        resp = client.post(
            "/api/v1/policy/chat",
            json={"session_id": _new_session_id(), "message": "粮食直补政策"},
            headers=_auth(token),
        )
        assert "[DONE]" in resp.text

    def test_chat_requires_auth(self, client: TestClient):
        resp = client.post(
            "/api/v1/policy/chat",
            json={"session_id": _new_session_id(), "message": "政策咨询"},
        )
        assert resp.status_code == 401

    def test_chat_empty_message_rejected(self, client: TestClient):
        token = _register_and_login(client, "policy_user4", "15000000004")
        resp = client.post(
            "/api/v1/policy/chat",
            json={"session_id": _new_session_id(), "message": ""},
            headers=_auth(token),
        )
        assert resp.status_code == 422

    def test_chat_missing_session_id(self, client: TestClient):
        token = _register_and_login(client, "policy_user5", "15000000005")
        resp = client.post(
            "/api/v1/policy/chat",
            json={"message": "政策咨询"},
            headers=_auth(token),
        )
        assert resp.status_code == 422

    def test_chat_persists_messages(self, client: TestClient):
        token = _register_and_login(client, "policy_user6", "15000000006")
        session_id = _new_session_id()
        client.post(
            "/api/v1/policy/chat",
            json={"session_id": session_id, "message": "种粮补贴怎么申请？"},
            headers=_auth(token),
        )
        sessions_resp = client.get("/api/v1/policy/sessions", headers=_auth(token))
        assert sessions_resp.status_code == 200
        sessions = sessions_resp.json()
        assert any(s["session_id"] == session_id for s in sessions)


# ── Sessions tests ────────────────────────────────────────────────────────────

class TestPolicySessions:
    def test_list_sessions_empty(self, client: TestClient):
        token = _register_and_login(client, "sessions_user1", "15100000001")
        resp = client.get("/api/v1/policy/sessions", headers=_auth(token))
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_sessions_requires_auth(self, client: TestClient):
        resp = client.get("/api/v1/policy/sessions")
        assert resp.status_code == 401

    def test_list_sessions_after_chat(self, client: TestClient):
        token = _register_and_login(client, "sessions_user2", "15100000002")
        session_id = _new_session_id()
        client.post(
            "/api/v1/policy/chat",
            json={"session_id": session_id, "message": "农业保险政策"},
            headers=_auth(token),
        )
        resp = client.get("/api/v1/policy/sessions", headers=_auth(token))
        assert resp.status_code == 200
        assert len(resp.json()) == 1
        assert resp.json()[0]["session_id"] == session_id

    def test_session_summary_schema(self, client: TestClient):
        token = _register_and_login(client, "sessions_user3", "15100000003")
        session_id = _new_session_id()
        client.post(
            "/api/v1/policy/chat",
            json={"session_id": session_id, "message": "惠农政策咨询"},
            headers=_auth(token),
        )
        sessions = client.get("/api/v1/policy/sessions", headers=_auth(token)).json()
        s = sessions[0]
        assert "session_id" in s
        assert "message_count" in s
        assert "last_message" in s
        assert "last_at" in s
        assert s["message_count"] >= 1

    def test_get_session_messages(self, client: TestClient):
        token = _register_and_login(client, "sessions_user4", "15100000004")
        session_id = _new_session_id()
        client.post(
            "/api/v1/policy/chat",
            json={"session_id": session_id, "message": "农业补贴怎么领"},
            headers=_auth(token),
        )
        resp = client.get(f"/api/v1/policy/sessions/{session_id}", headers=_auth(token))
        assert resp.status_code == 200
        messages = resp.json()
        assert len(messages) >= 2  # user + assistant messages
        roles = {m["role"] for m in messages}
        assert "user" in roles
        assert "assistant" in roles

    def test_get_session_messages_schema(self, client: TestClient):
        token = _register_and_login(client, "sessions_user5", "15100000005")
        session_id = _new_session_id()
        client.post(
            "/api/v1/policy/chat",
            json={"session_id": session_id, "message": "土地流转政策"},
            headers=_auth(token),
        )
        messages = client.get(
            f"/api/v1/policy/sessions/{session_id}", headers=_auth(token)
        ).json()
        for m in messages:
            assert "id" in m
            assert "session_id" in m
            assert "role" in m
            assert "content" in m
            assert "created_at" in m

    def test_get_nonexistent_session_returns_404(self, client: TestClient):
        token = _register_and_login(client, "sessions_user6", "15100000006")
        resp = client.get(
            f"/api/v1/policy/sessions/{_new_session_id()}",
            headers=_auth(token),
        )
        assert resp.status_code == 404

    def test_get_session_requires_auth(self, client: TestClient):
        resp = client.get(f"/api/v1/policy/sessions/{_new_session_id()}")
        assert resp.status_code == 401

    def test_sessions_isolated_between_users(self, client: TestClient):
        token_a = _register_and_login(client, "sessions_user7a", "15100000007")
        token_b = _register_and_login(client, "sessions_user7b", "15100000008")
        session_id = _new_session_id()
        client.post(
            "/api/v1/policy/chat",
            json={"session_id": session_id, "message": "补贴政策"},
            headers=_auth(token_a),
        )
        # User B should not see user A's session
        resp = client.get(
            f"/api/v1/policy/sessions/{session_id}", headers=_auth(token_b)
        )
        assert resp.status_code == 404


# ── Delete session tests ──────────────────────────────────────────────────────

class TestDeleteSession:
    def test_delete_session_success(self, client: TestClient):
        token = _register_and_login(client, "delete_user1", "15200000001")
        session_id = _new_session_id()
        client.post(
            "/api/v1/policy/chat",
            json={"session_id": session_id, "message": "政策咨询"},
            headers=_auth(token),
        )
        resp = client.delete(
            f"/api/v1/policy/sessions/{session_id}", headers=_auth(token)
        )
        assert resp.status_code == 204

    def test_delete_session_removes_messages(self, client: TestClient):
        token = _register_and_login(client, "delete_user2", "15200000002")
        session_id = _new_session_id()
        client.post(
            "/api/v1/policy/chat",
            json={"session_id": session_id, "message": "政策咨询"},
            headers=_auth(token),
        )
        client.delete(f"/api/v1/policy/sessions/{session_id}", headers=_auth(token))
        sessions = client.get("/api/v1/policy/sessions", headers=_auth(token)).json()
        assert not any(s["session_id"] == session_id for s in sessions)

    def test_delete_nonexistent_session_returns_404(self, client: TestClient):
        token = _register_and_login(client, "delete_user3", "15200000003")
        resp = client.delete(
            f"/api/v1/policy/sessions/{_new_session_id()}", headers=_auth(token)
        )
        assert resp.status_code == 404

    def test_delete_requires_auth(self, client: TestClient):
        resp = client.delete(f"/api/v1/policy/sessions/{_new_session_id()}")
        assert resp.status_code == 401


# ── SSE error-resilience tests ───────────────────────────────────────────────
# Verify that an exception raised inside the stream generator is swallowed
# by the try/except in _event_generator() and does NOT propagate as an
# ExceptionGroup out of sse_starlette's anyio task group.

class TestPolicyChatStreamErrorResilience:
    """
    Regression tests for ExceptionGroup: unhandled errors in a TaskGroup.

    When the underlying RAG stream raises a RuntimeError (e.g. LLM failure,
    DB error), the SSE endpoint must return 200 and emit a ``[ERROR]`` event
    instead of letting the exception escape into sse_starlette's anyio task group.
    """

    def test_stream_no_exception_group_on_runtime_error(
        self, client: TestClient
    ):
        """
        Simulate a RuntimeError inside run_policy_chat_stream.
        The endpoint must return 200, emit any partial chunks, then emit
        [ERROR] and not raise ExceptionGroup.
        """
        from unittest.mock import patch

        async def _failing_stream(*args, **kwargs):
            yield "政策"
            raise RuntimeError("simulated LLM failure")

        token = _register_and_login(client, "sse_err_policy1", "15800000001")

        with patch(
            "app.routers.policy.run_policy_chat_stream",
            side_effect=_failing_stream,
        ):
            resp = client.post(
                "/api/v1/policy/chat",
                json={"session_id": _new_session_id(), "message": "补贴政策"},
                headers=_auth(token),
            )

        # The server must not crash; 200 is the expected SSE start code
        assert resp.status_code == 200
        # The partial chunk before the error should be in the body
        assert "政策" in resp.text
        # The [ERROR] sentinel must be emitted to the client
        assert "[ERROR]" in resp.text

