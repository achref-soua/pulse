"""Derive the clinical scores a patient record supports — deterministically.

Grounding for the report/summary: rather than let the LLM narrate scores it
might invent, we compute every applicable score here from the structured record
using the same tested calculators the interactive risk tools use, and hand the
results to the narrator as facts. A score is only included when its inputs are
actually present (e.g. NEWS2 needs vitals) — we never guess a missing input.
"""

from __future__ import annotations

import dataclasses

from app.clinical.gas import GASInputs, compute_gas
from app.clinical.news2 import NEWS2Inputs, compute_news2
from app.clinical.rcri import RCRIInputs, compute_rcri
from app.models.patient import Patient


def _comorbid(p: Patient) -> object | None:
    return (p.comorbidities or [None])[0]


def compute_applicable_scores(p: Patient) -> dict[str, dict]:
    """Return {calculator_name: result_dict} for every score the record supports."""
    scores: dict[str, dict] = {}
    c = _comorbid(p)
    labs = sorted(p.labs or [], key=lambda x: x.taken_at, reverse=True)
    creatinine = next((lb.creatinine for lb in labs if lb.creatinine is not None), None)

    # NEWS2 — needs a vitals reading.
    vitals = sorted(p.vitals or [], key=lambda v: v.taken_at, reverse=True)
    if vitals:
        v = vitals[0]
        scores["NEWS2"] = dataclasses.asdict(compute_news2(NEWS2Inputs(
            respiration_rate=v.rr or 16,
            spo2=v.spo2 or 98.0,
            on_supplemental_oxygen=v.on_oxygen or False,
            systolic_bp=v.systolic_bp or 120,
            heart_rate=v.heart_rate or 70,
            consciousness=v.consciousness.value if v.consciousness else "A",
            temperature=v.temp_c or 36.5,
        )))

    # RCRI + GAS — need the comorbidity profile. Aortic surgery is high-risk vascular.
    if c is not None:
        scores["RCRI"] = dataclasses.asdict(compute_rcri(RCRIInputs(
            high_risk_surgery=True,
            ischemic_heart_disease=bool(c.cad or c.prior_mi),
            congestive_heart_failure=bool(c.chf),
            cerebrovascular_disease=bool(c.cvd_stroke),
            insulin_dependent_diabetes=bool(c.insulin_dependent),
            preop_creatinine_gt_2=creatinine is not None and creatinine > 2.0,
        )))
        scores["GAS"] = dataclasses.asdict(compute_gas(GASInputs(
            age=p.age,
            shock=bool(vitals and (vitals[0].systolic_bp or 120) < 90),
            myocardial_disease=bool(c.cad or c.prior_mi or c.chf),
            cerebrovascular_disease=bool(c.cvd_stroke),
            renal_disease=bool(c.ckd) or (creatinine is not None and creatinine > 2.0),
        )))

    return scores


def scores_as_text(scores: dict[str, dict]) -> str:
    """Flatten computed scores into a fact block the narrator must not contradict."""
    if not scores:
        return "No scores could be computed from the available record."
    lines = []
    for name, val in scores.items():
        score = val.get("score", val.get("total_score", "—"))
        cls = val.get("risk_class") or val.get("risk_category") or val.get("response_level") \
            or val.get("risk_interpretation") or ""
        lines.append(f"- {name}: {score}" + (f" ({cls})" if cls else ""))
    return "\n".join(lines)
