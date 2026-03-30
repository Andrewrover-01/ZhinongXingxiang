import io

import pytest
from fastapi.testclient import TestClient


def _register_and_login(client: TestClient, username: str, phone: str) -> str:
    client.post(
        "/api/v1/auth/register",
        json={"username": username, "phone": phone, "password": "pass1234"},
    )
    resp = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": "pass1234"},
    )
    return resp.json()["access_token"]


def test_upload_image(client: TestClient, tmp_path):
    token = _register_and_login(client, "upload_user", "13222222001")
    fake_image = io.BytesIO(b"\xff\xd8\xff" + b"\x00" * 100)  # minimal JPEG-like bytes
    resp = client.post(
        "/api/v1/upload/image",
        files={"file": ("test.jpg", fake_image, "image/jpeg")},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "url" in data
    assert data["content_type"] == "image/jpeg"


def test_upload_invalid_type(client: TestClient):
    token = _register_and_login(client, "upload_invalid", "13222222002")
    resp = client.post(
        "/api/v1/upload/image",
        files={"file": ("malware.exe", b"MZ\x90\x00", "application/octet-stream")},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 400


def test_upload_unauthenticated(client: TestClient):
    resp = client.post(
        "/api/v1/upload/image",
        files={"file": ("test.jpg", b"\xff\xd8\xff", "image/jpeg")},
    )
    assert resp.status_code == 403
