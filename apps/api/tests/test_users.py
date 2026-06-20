import pytest


async def _make_user(client, email: str, password: str, role: str) -> dict:
    await client.post(
        "/auth/register",
        json={"email": email, "password": password, "full_name": "Test", "role": role},
    )
    resp = await client.post("/auth/login", json={"email": email, "password": password})
    data = resp.json()
    return {"Authorization": f"Bearer {data['access_token']}"}


@pytest.mark.anyio
async def test_list_users_requires_admin(client):
    headers = await _make_user(client, "nurse-u@test.pulse", "nurse-pass-123", "nurse")
    resp = await client.get("/users", headers=headers)
    assert resp.status_code == 403


@pytest.mark.anyio
async def test_list_users_as_admin(client):
    headers = await _make_user(client, "admin-u@test.pulse", "admin-pass-123", "admin")
    resp = await client.get("/users", headers=headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.anyio
async def test_update_role_not_found(client):
    headers = await _make_user(client, "admin-u2@test.pulse", "admin-pass-456", "admin")
    resp = await client.patch(
        "/users/00000000-0000-0000-0000-000000000000/role",
        json={"role": "nurse"},
        headers=headers,
    )
    assert resp.status_code == 404


@pytest.mark.anyio
async def test_audit_log_requires_admin(client):
    headers = await _make_user(client, "surgeon-u@test.pulse", "surgeon-pass-123", "surgeon")
    resp = await client.get("/users/audit-log", headers=headers)
    assert resp.status_code == 403


@pytest.mark.anyio
async def test_audit_log_as_admin(client):
    headers = await _make_user(client, "admin-u3@test.pulse", "admin-pass-789", "admin")
    resp = await client.get("/users/audit-log", headers=headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
