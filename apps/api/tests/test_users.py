import pytest

from app.core.security import hash_password
from app.models.user import User, UserRole


async def _make_user(client, email: str, password: str) -> dict:
    """Self-register (always a nurse) and return auth headers."""
    await client.post(
        "/auth/register",
        json={"email": email, "password": password, "full_name": "Test"},
    )
    resp = await client.post("/auth/login", json={"email": email, "password": password})
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


async def _admin_header(client, db, email: str, password: str) -> dict:
    """Seed a genuine admin directly (self-registration can never create one) and log in."""
    db.add(
        User(
            email=email,
            hashed_password=hash_password(password),
            full_name="Test Admin",
            role=UserRole.admin,
        )
    )
    await db.flush()
    resp = await client.post("/auth/login", json={"email": email, "password": password})
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


@pytest.mark.anyio
async def test_list_users_requires_admin(client):
    headers = await _make_user(client, "nurse-u@test.pulse", "nurse-pass-123")
    resp = await client.get("/users", headers=headers)
    assert resp.status_code == 403


@pytest.mark.anyio
async def test_list_users_as_admin(client, db):
    headers = await _admin_header(client, db, "admin-u@test.pulse", "admin-pass-123")
    resp = await client.get("/users", headers=headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.anyio
async def test_update_role_not_found(client, db):
    headers = await _admin_header(client, db, "admin-u2@test.pulse", "admin-pass-456")
    resp = await client.patch(
        "/users/00000000-0000-0000-0000-000000000000/role",
        json={"role": "nurse"},
        headers=headers,
    )
    assert resp.status_code == 404


@pytest.mark.anyio
async def test_audit_log_requires_admin(client):
    headers = await _make_user(client, "surgeon-u@test.pulse", "surgeon-pass-123")
    resp = await client.get("/users/audit-log", headers=headers)
    assert resp.status_code == 403


@pytest.mark.anyio
async def test_audit_log_as_admin(client, db):
    headers = await _admin_header(client, db, "admin-u3@test.pulse", "admin-pass-789")
    resp = await client.get("/users/audit-log", headers=headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
