import pytest


async def _auth_header(client, email: str, password: str) -> dict:
    await client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
            "full_name": "Dashboard Tester",
            "role": "surgeon",
        },
    )
    resp = await client.post("/auth/login", json={"email": email, "password": password})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.anyio
async def test_dashboard_stats_structure(client):
    headers = await _auth_header(client, "dash@test.pulse", "dashboard-pass-123")
    resp = await client.get("/dashboard/stats", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "total_patients" in data
    assert "by_phase" in data
    assert "pre" in data["by_phase"]
    assert "intra" in data["by_phase"]
    assert "post" in data["by_phase"]
    assert "high_news2_count" in data
    assert "borderline_anatomy_count" in data
    assert "challenging_anatomy_count" in data
    assert "upcoming_procedures" in data


@pytest.mark.anyio
async def test_dashboard_stats_requires_auth(client):
    resp = await client.get("/dashboard/stats")
    assert resp.status_code == 403


@pytest.mark.anyio
async def test_dashboard_counts_non_negative(client):
    headers = await _auth_header(client, "dash2@test.pulse", "dashboard-pass-456")
    resp = await client.get("/dashboard/stats", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_patients"] >= 0
    assert data["high_news2_count"] >= 0
    assert data["borderline_anatomy_count"] >= 0
    assert data["challenging_anatomy_count"] >= 0
    assert data["upcoming_procedures"] >= 0
    bp = data["by_phase"]
    assert bp["pre"] + bp["intra"] + bp["post"] == data["total_patients"]
