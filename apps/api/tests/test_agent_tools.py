"""Agent tool layer — grounding + DB wiring.

Tools are LangChain @tool objects; call them via ``.ainvoke({...})`` which
exercises the same schema path the LangGraph ToolNode uses.
"""

import pytest

from app.ai import tools
from app.clinical.rcri import RCRIInputs, compute_rcri
from app.models.device import Device
from app.models.patient import AneurysmType, Patient, Phase, PlannedIntervention
from app.models.vital import Vital


@pytest.mark.asyncio
async def test_calculate_risk_score_matches_calculator():
    inputs = {
        "high_risk_surgery": True,
        "ischemic_heart_disease": True,
        "congestive_heart_failure": False,
        "cerebrovascular_disease": False,
        "insulin_dependent_diabetes": False,
        "preop_creatinine_gt_2": False,
    }
    out = await tools.calculate_risk_score.ainvoke({"kind": "rcri", "inputs": inputs})
    expected = compute_rcri(RCRIInputs(**inputs))
    assert out["score"] == expected.score == 2
    assert out["risk_class"] == expected.risk_class


@pytest.mark.asyncio
async def test_calculate_risk_score_rejects_unknown_and_bad_inputs():
    assert "error" in await tools.calculate_risk_score.ainvoke({"kind": "nope", "inputs": {}})
    assert "error" in await tools.calculate_risk_score.ainvoke({"kind": "rcri", "inputs": {"x": 1}})


async def _seed_patient(db) -> Patient:
    p = Patient(
        patient_id="P-9001", name="Test Aorta", age=74, sex="M", mrn="MRN-9001",
        aneurysm_type=AneurysmType.infrarenal_aaa, max_diameter_mm=58.0, location="infrarenal",
        neck_length_mm=18.0, neck_angulation_deg=45.0, neck_diameter_mm=24.0,
        iliac_access_min_mm=8.0, iliac_access_max_mm=11.0,
        phase=Phase.pre, planned_intervention=PlannedIntervention.evar,
    )
    db.add(p)
    await db.flush()
    db.add(Vital(patient_id=p.id, taken_at=__import__("datetime").datetime(2026, 1, 1),
                 rr=20, spo2=95.0, systolic_bp=104, heart_rate=92, temp_c=37.1))
    await db.flush()
    return p


@pytest.mark.asyncio
async def test_get_patient_and_query_cohort(db):
    tools.bind_db(db)
    await _seed_patient(db)

    rec = await tools.get_patient.ainvoke({"patient_id": "P-9001"})
    assert rec["patient_id"] == "P-9001"
    assert rec["latest_vitals"]["respiration_rate"] == 20
    assert rec["anatomy"]["neck_length_mm"] == 18.0

    assert "error" in await tools.get_patient.ainvoke({"patient_id": "P-0000"})

    cohort = await tools.query_cohort.ainvoke({"filters": {"phase": "pre"}})
    assert cohort["total"] == 1
    assert cohort["by_intervention"].get("EVAR") == 1


@pytest.mark.asyncio
async def test_match_devices_ranks_catalog(db):
    tools.bind_db(db)
    await _seed_patient(db)
    db.add(Device(
        manufacturer="Acme", name="AortaFit-1", indication="EVAR",
        ifu_proximal_min_mm=18.0, ifu_proximal_max_mm=32.0,
        ifu_distal_min_mm=8.0, ifu_distal_max_mm=25.0, ifu_length_options_mm=[],
        ifu_min_neck_length_mm=10.0, ifu_max_neck_angulation_deg=60.0,
        ifu_iliac_min_mm=6.0, ifu_iliac_max_mm=25.0, sheath_fr=18,
    ))
    await db.flush()

    out = await tools.match_devices.ainvoke({"patient_id": "P-9001"})
    assert out["patient_id"] == "P-9001"
    assert len(out["devices"]) == 1
    assert out["devices"][0]["overall"] == "suitable"
