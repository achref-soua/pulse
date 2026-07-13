"""Cohort analytics aggregates."""

import pytest

from app.models.patient import AneurysmType, Patient, Phase, PlannedIntervention


def _p(pid: str, **kw) -> Patient:
    base = {
        "name": f"P {pid}", "age": 72, "sex": "M", "mrn": f"MRN-{pid}",
        "aneurysm_type": AneurysmType.infrarenal_aaa, "max_diameter_mm": 57.0,
        "phase": Phase.pre, "planned_intervention": PlannedIntervention.evar,
    }
    base.update(kw)
    return Patient(patient_id=pid, **base)


async def _token(client, db):
    from app.core.security import hash_password
    from app.models.user import User, UserRole
    db.add(User(email="an-surgeon@test.pulse", hashed_password=hash_password("pw"),
                full_name="S", role=UserRole.surgeon))
    await db.flush()
    r = await client.post("/auth/login", json={"email": "an-surgeon@test.pulse", "password": "pw"})
    return r.json()["access_token"]


@pytest.mark.asyncio
async def test_overview_distributions(client, db):
    db.add_all([
        _p("A1", age=55, max_diameter_mm=48.0, phase=Phase.pre),
        _p("A2", age=65, max_diameter_mm=57.0, phase=Phase.post,
           planned_intervention=PlannedIntervention.tevar, sex="F"),
        _p("A3", age=82, max_diameter_mm=62.0, phase=Phase.post),
    ])
    await db.flush()
    token = await _token(client, db)

    r = await client.get("/analytics/overview", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 3
    assert data["by_phase"]["post"] == 2
    assert data["by_intervention"]["EVAR"] == 2
    assert data["by_sex"] == {"M": 2, "F": 1}
    assert data["by_diameter_band"]["<50"] == 1
    assert data["by_diameter_band"]["≥60"] == 1
    assert data["by_age_band"]["≥80"] == 1


@pytest.mark.asyncio
async def test_overview_requires_auth(client):
    assert (await client.get("/analytics/overview")).status_code == 401
