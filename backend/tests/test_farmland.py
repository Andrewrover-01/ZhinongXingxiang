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


def test_create_farmland(client: TestClient):
    token = _register_and_login(client, "farm_create", "13111111001")
    resp = client.post(
        "/api/v1/farmlands/",
        json={"name": "东头二亩地", "area": "2.50", "crop_type": "水稻", "location": "湖南省长沙市"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "东头二亩地"
    assert float(data["area"]) == 2.50


def test_list_farmlands(client: TestClient):
    token = _register_and_login(client, "farm_list", "13111111002")
    for i in range(3):
        client.post(
            "/api/v1/farmlands/",
            json={"name": f"地块{i}", "area": str(i + 1)},
            headers={"Authorization": f"Bearer {token}"},
        )
    resp = client.get("/api/v1/farmlands/", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert len(resp.json()) == 3


def test_get_farmland(client: TestClient):
    token = _register_and_login(client, "farm_get", "13111111003")
    create_resp = client.post(
        "/api/v1/farmlands/",
        json={"name": "北边大田", "area": "5.00"},
        headers={"Authorization": f"Bearer {token}"},
    )
    farmland_id = create_resp.json()["id"]
    resp = client.get(
        f"/api/v1/farmlands/{farmland_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["id"] == farmland_id


def test_update_farmland(client: TestClient):
    token = _register_and_login(client, "farm_update", "13111111004")
    create_resp = client.post(
        "/api/v1/farmlands/",
        json={"name": "待更新地块", "area": "3.00"},
        headers={"Authorization": f"Bearer {token}"},
    )
    farmland_id = create_resp.json()["id"]
    resp = client.put(
        f"/api/v1/farmlands/{farmland_id}",
        json={"name": "已更新地块", "crop_type": "玉米"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "已更新地块"
    assert resp.json()["crop_type"] == "玉米"


def test_delete_farmland(client: TestClient):
    token = _register_and_login(client, "farm_delete", "13111111005")
    create_resp = client.post(
        "/api/v1/farmlands/",
        json={"name": "待删除地块", "area": "1.00"},
        headers={"Authorization": f"Bearer {token}"},
    )
    farmland_id = create_resp.json()["id"]
    del_resp = client.delete(
        f"/api/v1/farmlands/{farmland_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert del_resp.status_code == 204
    get_resp = client.get(
        f"/api/v1/farmlands/{farmland_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_resp.status_code == 404


def test_farmland_isolation(client: TestClient):
    """用户只能访问自己的农田"""
    token_a = _register_and_login(client, "farm_iso_a", "13111111006")
    token_b = _register_and_login(client, "farm_iso_b", "13111111007")
    create_resp = client.post(
        "/api/v1/farmlands/",
        json={"name": "用户A的地块", "area": "2.00"},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    farmland_id = create_resp.json()["id"]
    resp = client.get(
        f"/api/v1/farmlands/{farmland_id}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert resp.status_code == 404


def test_farmland_unauthenticated(client: TestClient):
    resp = client.get("/api/v1/farmlands/")
    assert resp.status_code == 401
