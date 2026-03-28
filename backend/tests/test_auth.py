import pytest
from fastapi.testclient import TestClient


def test_register_success(client: TestClient):
    resp = client.post(
        "/api/v1/auth/register",
        json={
            "username": "farmer01",
            "phone": "13800138001",
            "password": "secret123",
            "real_name": "张三",
            "province": "湖南省",
            "city": "长沙市",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["username"] == "farmer01"
    assert data["phone"] == "13800138001"
    assert "password" not in data
    assert "password_hash" not in data


def test_register_duplicate_username(client: TestClient):
    payload = {"username": "dup_user", "phone": "13800138002", "password": "secret123"}
    client.post("/api/v1/auth/register", json=payload)
    resp = client.post(
        "/api/v1/auth/register",
        json={"username": "dup_user", "phone": "13800138099", "password": "anotherpass"},
    )
    assert resp.status_code == 400
    assert "用户名" in resp.json()["detail"]


def test_register_duplicate_phone(client: TestClient):
    client.post(
        "/api/v1/auth/register",
        json={"username": "user_phone_a", "phone": "13900139001", "password": "secret123"},
    )
    resp = client.post(
        "/api/v1/auth/register",
        json={"username": "user_phone_b", "phone": "13900139001", "password": "secret123"},
    )
    assert resp.status_code == 400
    assert "手机号" in resp.json()["detail"]


def test_login_success(client: TestClient):
    client.post(
        "/api/v1/auth/register",
        json={"username": "login_user", "phone": "13700137001", "password": "mypassword"},
    )
    resp = client.post(
        "/api/v1/auth/login",
        json={"username": "login_user", "password": "mypassword"},
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()
    assert resp.json()["token_type"] == "bearer"


def test_login_with_phone(client: TestClient):
    client.post(
        "/api/v1/auth/register",
        json={"username": "phone_login_user", "phone": "13700137002", "password": "mypassword"},
    )
    resp = client.post(
        "/api/v1/auth/login",
        json={"username": "13700137002", "password": "mypassword"},
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password(client: TestClient):
    client.post(
        "/api/v1/auth/register",
        json={"username": "wrong_pw_user", "phone": "13600136001", "password": "correct"},
    )
    resp = client.post(
        "/api/v1/auth/login",
        json={"username": "wrong_pw_user", "password": "incorrect"},
    )
    assert resp.status_code == 401


def test_get_me(client: TestClient):
    client.post(
        "/api/v1/auth/register",
        json={"username": "me_user", "phone": "13500135001", "password": "pass1234"},
    )
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"username": "me_user", "password": "pass1234"},
    )
    token = login_resp.json()["access_token"]
    resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["username"] == "me_user"


def test_get_me_unauthorized(client: TestClient):
    resp = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid_token"})
    assert resp.status_code == 401
