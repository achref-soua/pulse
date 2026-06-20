import pytest


@pytest.mark.anyio
async def test_register_and_login(client):
    reg = await client.post("/auth/register", json={
        "email": "newuser@test.pulse",
        "password": "secure-password-123",
        "full_name": "New User",
        "role": "nurse",
    })
    assert reg.status_code == 201
    data = reg.json()
    assert data["email"] == "newuser@test.pulse"
    assert data["role"] == "nurse"

    login = await client.post("/auth/login", json={
        "email": "newuser@test.pulse",
        "password": "secure-password-123",
    })
    assert login.status_code == 200
    tokens = login.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["token_type"] == "bearer"


@pytest.mark.anyio
async def test_login_invalid_credentials(client):
    await client.post("/auth/register", json={
        "email": "another@test.pulse",
        "password": "correct-password",
        "full_name": "Another User",
        "role": "nurse",
    })
    resp = await client.post("/auth/login", json={
        "email": "another@test.pulse",
        "password": "wrong-password",
    })
    assert resp.status_code == 401


@pytest.mark.anyio
async def test_refresh_token(client):
    await client.post("/auth/register", json={
        "email": "refresh@test.pulse",
        "password": "pass-word-123",
        "full_name": "Refresh User",
        "role": "nurse",
    })
    login = await client.post("/auth/login", json={
        "email": "refresh@test.pulse",
        "password": "pass-word-123",
    })
    tokens = login.json()

    refresh = await client.post("/auth/refresh", json={
        "refresh_token": tokens["refresh_token"]
    })
    assert refresh.status_code == 200
    assert "access_token" in refresh.json()
