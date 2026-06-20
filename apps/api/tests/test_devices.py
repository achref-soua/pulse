import pytest


async def _auth_header(client, email: str, password: str) -> dict:
    await client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
            "full_name": "Device Tester",
            "role": "surgeon",
        },
    )
    resp = await client.post("/auth/login", json={"email": email, "password": password})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.anyio
async def test_list_devices_requires_auth(client):
    resp = await client.get("/devices")
    assert resp.status_code == 403


@pytest.mark.anyio
async def test_list_devices_empty_db(client):
    headers = await _auth_header(client, "dev@test.pulse", "devices-pass-123")
    resp = await client.get("/devices", headers=headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.anyio
async def test_get_device_not_found(client):
    headers = await _auth_header(client, "dev2@test.pulse", "devices-pass-456")
    resp = await client.get("/devices/00000000-0000-0000-0000-000000000000", headers=headers)
    assert resp.status_code == 404
