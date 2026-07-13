"""Grounded score derivation — the report/summary never lets the LLM invent a score."""

import datetime

from app.ai.scoring import compute_applicable_scores, scores_as_text
from app.models.comorbidity import Comorbidity
from app.models.lab import Lab
from app.models.patient import AneurysmType, Patient, Phase, PlannedIntervention
from app.models.vital import Vital


def _patient(**kw) -> Patient:
    p = Patient(
        patient_id="P-7001", name="Score Test", age=78, sex="M", mrn="MRN-7001",
        aneurysm_type=AneurysmType.infrarenal_aaa, max_diameter_mm=60.0,
        phase=Phase.pre, planned_intervention=PlannedIntervention.evar,
    )
    for k, v in kw.items():
        setattr(p, k, v)
    return p


def test_scores_computed_from_full_record():
    p = _patient(
        comorbidities=[Comorbidity(cad=True, chf=False, cvd_stroke=True,
                                   insulin_dependent=True, ckd=True)],
        vitals=[Vital(taken_at=datetime.datetime(2026, 1, 1), rr=22, spo2=93.0,
                      systolic_bp=100, heart_rate=95, temp_c=37.2)],
        labs=[Lab(taken_at=datetime.datetime(2026, 1, 1), creatinine=2.5)],
    )
    scores = compute_applicable_scores(p)

    assert set(scores) == {"NEWS2", "RCRI", "GAS"}
    # RCRI: high-risk surgery + IHD(cad) + CVD + insulin DM + creatinine>2 = 5 factors
    assert scores["RCRI"]["score"] == 5
    assert scores["GAS"]["score"] > p.age  # age plus weighted comorbidity points
    text = scores_as_text(scores)
    assert "RCRI: 5" in text and "NEWS2" in text


def test_only_applicable_scores_included():
    # No comorbidities, no vitals → nothing derivable.
    assert compute_applicable_scores(_patient(comorbidities=[], vitals=[], labs=[])) == {}
    # Vitals only → NEWS2 only (RCRI/GAS need the comorbidity profile).
    p = _patient(comorbidities=[], labs=[],
                 vitals=[Vital(taken_at=datetime.datetime(2026, 1, 1), rr=18, spo2=97.0,
                               systolic_bp=130, heart_rate=72, temp_c=36.6)])
    assert set(compute_applicable_scores(p)) == {"NEWS2"}
    assert scores_as_text({}) == "No scores could be computed from the available record."
