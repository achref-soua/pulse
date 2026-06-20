"""Integration-level tests for the /risk/* endpoints."""

import pytest
from httpx import AsyncClient

from app.core.security import create_access_token
from app.models.user import User


def _token_headers(user: User) -> dict[str, str]:
    token = create_access_token(str(user.id), user.role.value)
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.anyio
async def test_rcri_zero_factors(client: AsyncClient, surgeon_user: User):
    resp = await client.post(
        "/risk/rcri",
        json={
            "high_risk_surgery": False,
            "ischemic_heart_disease": False,
            "congestive_heart_failure": False,
            "cerebrovascular_disease": False,
            "insulin_dependent_diabetes": False,
            "preop_creatinine_gt_2": False,
        },
        headers=_token_headers(surgeon_user),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["score"] == 0
    assert data["risk_class"] == "I"
    assert data["estimated_risk_pct"] == pytest.approx(0.4)


@pytest.mark.anyio
async def test_rcri_four_factors(client: AsyncClient, surgeon_user: User):
    resp = await client.post(
        "/risk/rcri",
        json={
            "high_risk_surgery": True,
            "ischemic_heart_disease": True,
            "congestive_heart_failure": True,
            "cerebrovascular_disease": True,
            "insulin_dependent_diabetes": False,
            "preop_creatinine_gt_2": False,
        },
        headers=_token_headers(surgeon_user),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["score"] == 4
    assert data["risk_class"] == "IV"
    assert data["estimated_risk_pct"] == pytest.approx(5.4)


@pytest.mark.anyio
async def test_rcri_requires_auth(client: AsyncClient):
    resp = await client.post(
        "/risk/rcri",
        json={
            "high_risk_surgery": False,
            "ischemic_heart_disease": False,
            "congestive_heart_failure": False,
            "cerebrovascular_disease": False,
            "insulin_dependent_diabetes": False,
            "preop_creatinine_gt_2": False,
        },
    )
    assert resp.status_code == 401


@pytest.mark.anyio
async def test_news2_low(client: AsyncClient, surgeon_user: User):
    resp = await client.post(
        "/risk/news2",
        json={
            "respiration_rate": 16,
            "spo2": 97,
            "on_supplemental_oxygen": False,
            "systolic_bp": 120,
            "heart_rate": 75,
            "consciousness": "A",
            "temperature": 37.0,
        },
        headers=_token_headers(surgeon_user),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_score"] == 0
    assert data["response_level"] == "Low"


@pytest.mark.anyio
async def test_news2_high(client: AsyncClient, surgeon_user: User):
    resp = await client.post(
        "/risk/news2",
        json={
            "respiration_rate": 30,
            "spo2": 91,
            "on_supplemental_oxygen": True,
            "systolic_bp": 85,
            "heart_rate": 130,
            "consciousness": "V",
            "temperature": 38.9,
        },
        headers=_token_headers(surgeon_user),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_score"] >= 7
    assert data["response_level"] == "High"


@pytest.mark.anyio
async def test_cha2ds2_vasc(client: AsyncClient, surgeon_user: User):
    resp = await client.post(
        "/risk/cha2ds2-vasc",
        json={
            "congestive_heart_failure": True,
            "hypertension": True,
            "age_75_or_over": False,
            "diabetes_mellitus": True,
            "stroke_or_tia": False,
            "vascular_disease": False,
            "age_65_to_74": True,
            "female_sex": False,
        },
        headers=_token_headers(surgeon_user),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["score"] == 4


@pytest.mark.anyio
async def test_has_bled(client: AsyncClient, surgeon_user: User):
    resp = await client.post(
        "/risk/has-bled",
        json={
            "hypertension_uncontrolled": True,
            "renal_dysfunction": False,
            "liver_dysfunction": False,
            "stroke_history": True,
            "bleeding_predisposition": False,
            "labile_inr": False,
            "elderly": True,
            "antiplatelet_or_nsaid": False,
            "alcohol": False,
        },
        headers=_token_headers(surgeon_user),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["score"] == 3


@pytest.mark.anyio
async def test_gas_score(client: AsyncClient, surgeon_user: User):
    resp = await client.post(
        "/risk/gas",
        json={
            "age": 72,
            "shock": False,
            "myocardial_disease": False,
            "cerebrovascular_disease": False,
            "renal_disease": False,
        },
        headers=_token_headers(surgeon_user),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["score"] == 72
    assert "risk_interpretation" in data


@pytest.mark.anyio
async def test_euroscore2(client: AsyncClient, surgeon_user: User):
    resp = await client.post(
        "/risk/euroscore2",
        json={
            "age": 70,
            "female": False,
            "renal_dysfunction": "none",
            "extracardiac_arteriopathy": True,
            "poor_mobility": False,
            "previous_cardiac_surgery": False,
            "chronic_lung_disease": False,
            "active_endocarditis": False,
            "critical_preop_state": False,
            "diabetes_on_insulin": False,
            "nyha_class": 2,
            "ccs_angina": 0,
            "ejection_fraction_pct": 55.0,
            "recent_mi": False,
            "pulmonary_hypertension": "none",
            "emergency": False,
            "other_than_isolated_cabg": False,
            "thoracic_aorta_surgery": True,
        },
        headers=_token_headers(surgeon_user),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "predicted_mortality_pct" in data
    assert data["predicted_mortality_pct"] > 0


@pytest.mark.anyio
async def test_ifu_fit_suitable(client: AsyncClient, surgeon_user: User):
    body = {
        "neck_length_mm": 20.0,
        "neck_angulation_deg": 30.0,
        "neck_diameter_mm": 24.0,
        "iliac_access_min_mm": 10.0,
        "max_diameter_mm": 60.0,
        "devices": [
            {
                "name": "EndoFlex AAA-I",
                "ifu_min_neck_length_mm": 10.0,
                "ifu_max_neck_angulation_deg": 75.0,
                "ifu_proximal_min_mm": 17.0,
                "ifu_proximal_max_mm": 31.0,
                "ifu_iliac_min_mm": 6.0,
                "ifu_iliac_max_mm": 25.0,
                "ifu_distal_min_mm": 7.5,
                "ifu_distal_max_mm": 22.0,
            }
        ],
    }
    resp = await client.post("/risk/ifu-fit", json=body, headers=_token_headers(surgeon_user))
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["overall"] == "suitable"


@pytest.mark.anyio
async def test_ifu_fit_contraindicated(client: AsyncClient, surgeon_user: User):
    body = {
        "neck_length_mm": 3.0,
        "neck_angulation_deg": 85.0,
        "neck_diameter_mm": 24.0,
        "iliac_access_min_mm": 10.0,
        "max_diameter_mm": 70.0,
        "devices": [
            {
                "name": "EndoFlex AAA-I",
                "ifu_min_neck_length_mm": 10.0,
                "ifu_max_neck_angulation_deg": 75.0,
                "ifu_proximal_min_mm": 17.0,
                "ifu_proximal_max_mm": 31.0,
                "ifu_iliac_min_mm": 6.0,
                "ifu_iliac_max_mm": 25.0,
                "ifu_distal_min_mm": 7.5,
                "ifu_distal_max_mm": 22.0,
            }
        ],
    }
    resp = await client.post("/risk/ifu-fit", json=body, headers=_token_headers(surgeon_user))
    assert resp.status_code == 200
    data = resp.json()
    assert data[0]["overall"] == "contraindicated"
