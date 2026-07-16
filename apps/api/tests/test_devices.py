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
    assert resp.status_code == 401


@pytest.mark.anyio
async def test_list_devices_empty_db(client):
    headers = await _auth_header(client, "dev@test.pulse", "devices-pass-123")
    resp = await client.get("/devices", headers=headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.anyio
async def test_list_devices_serializes_seeded_device(client, db):
    """A real device must serialize — the id is a UUID, which the response model must accept."""
    from app.models.device import Device

    db.add(Device(
        manufacturer="Acme", name="AortaFit-1", indication="EVAR",
        ifu_proximal_min_mm=18.0, ifu_proximal_max_mm=32.0,
        ifu_distal_min_mm=8.0, ifu_distal_max_mm=25.0, ifu_length_options_mm=[],
        ifu_min_neck_length_mm=10.0, ifu_max_neck_angulation_deg=60.0,
        ifu_iliac_min_mm=6.0, ifu_iliac_max_mm=25.0, sheath_fr=18,
    ))
    await db.flush()
    headers = await _auth_header(client, "dev-seed@test.pulse", "devices-pass-123")
    resp = await client.get("/devices", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 1
    assert body[0]["name"] == "AortaFit-1"
    assert isinstance(body[0]["id"], str)  # UUID serialized to string


@pytest.mark.anyio
async def test_get_device_not_found(client):
    headers = await _auth_header(client, "dev2@test.pulse", "devices-pass-456")
    resp = await client.get("/devices/00000000-0000-0000-0000-000000000000", headers=headers)
    assert resp.status_code == 404
