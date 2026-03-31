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


# Minimal valid magic bytes for each supported image type
_JPEG_MAGIC = b"\xff\xd8\xff" + b"\x00" * 100
_PNG_MAGIC = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
_WEBP_MAGIC = b"RIFF\x10\x00\x00\x00WEBP" + b"\x00" * 100
_GIF87_MAGIC = b"GIF87a" + b"\x00" * 100
_GIF89_MAGIC = b"GIF89a" + b"\x00" * 100


def test_upload_image(client: TestClient, tmp_path):
    token = _register_and_login(client, "upload_user", "13222222001")
    resp = client.post(
        "/api/v1/upload/image",
        files={"file": ("test.jpg", io.BytesIO(_JPEG_MAGIC), "image/jpeg")},
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
    assert resp.status_code == 401


# --- MED-003: magic bytes validation ---

def test_upload_spoofed_content_type_rejected(client: TestClient):
    """A file with wrong magic bytes but correct Content-Type must be rejected."""
    token = _register_and_login(client, "upload_spoof", "13222222003")
    # Send EXE magic bytes (MZ header) but claim image/jpeg
    resp = client.post(
        "/api/v1/upload/image",
        files={"file": ("evil.jpg", b"MZ\x90\x00" + b"\x00" * 100, "image/jpeg")},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 400
    assert "格式不符" in resp.json()["detail"]


def test_upload_png_magic_accepted(client: TestClient):
    token = _register_and_login(client, "upload_png", "13222222004")
    resp = client.post(
        "/api/v1/upload/image",
        files={"file": ("test.png", io.BytesIO(_PNG_MAGIC), "image/png")},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201


def test_upload_webp_magic_accepted(client: TestClient):
    token = _register_and_login(client, "upload_webp", "13222222005")
    resp = client.post(
        "/api/v1/upload/image",
        files={"file": ("test.webp", io.BytesIO(_WEBP_MAGIC), "image/webp")},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201


def test_upload_gif87_magic_accepted(client: TestClient):
    token = _register_and_login(client, "upload_gif87", "13222222006")
    resp = client.post(
        "/api/v1/upload/image",
        files={"file": ("test.gif", io.BytesIO(_GIF87_MAGIC), "image/gif")},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201


def test_upload_gif89_magic_accepted(client: TestClient):
    token = _register_and_login(client, "upload_gif89", "13222222007")
    resp = client.post(
        "/api/v1/upload/image",
        files={"file": ("test.gif", io.BytesIO(_GIF89_MAGIC), "image/gif")},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201


# --- MED-001: weak default SECRET_KEY in production ---

def test_weak_secret_key_rejected_in_production():
    """Settings must raise ValueError when APP_ENV=production with the default weak key."""
    import os
    from importlib import import_module

    env_backup = os.environ.copy()
    try:
        os.environ["APP_ENV"] = "production"
        os.environ.pop("SECRET_KEY", None)  # ensure the default is used
        # Reimport Settings directly to pick up the env override
        from app.core.config import Settings
        with pytest.raises(Exception):
            Settings()
    finally:
        os.environ.clear()
        os.environ.update(env_backup)


def test_strong_secret_key_accepted_in_production():
    """Settings must not raise when APP_ENV=production with a custom SECRET_KEY."""
    import os

    env_backup = os.environ.copy()
    try:
        os.environ["APP_ENV"] = "production"
        os.environ["SECRET_KEY"] = "a-very-strong-random-key-for-testing-purposes-only"
        os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost/testdb"
        from app.core.config import Settings
        s = Settings()
        assert s.SECRET_KEY == "a-very-strong-random-key-for-testing-purposes-only"
    finally:
        os.environ.clear()
        os.environ.update(env_backup)
