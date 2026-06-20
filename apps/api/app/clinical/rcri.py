"""Revised Cardiac Risk Index (Lee Index).

Reference: Lee TH, et al. Circulation. 1999;100(10):1043-1049.
See docs/clinical/REFERENCES.md for full citation.
"""

from dataclasses import dataclass


@dataclass
class RCRIInputs:
    high_risk_surgery: bool  # intraperitoneal, intrathoracic, or suprainguinal vascular
    ischemic_heart_disease: bool  # history of MI, positive ETT, angina, nitrates, Q-waves
    congestive_heart_failure: bool  # history of CHF, pulmonary edema, PND, or S3/bilateral rales
    cerebrovascular_disease: bool  # history of TIA or stroke
    insulin_dependent_diabetes: bool
    preop_creatinine_gt_2: bool  # serum creatinine > 2.0 mg/dL (> 177 µmol/L)


@dataclass
class RCRIResult:
    score: int
    risk_class: str  # I, II, III, IV
    estimated_risk_pct: float
    factors_present: list[str]


_RISK_TABLE = [
    (0, "I", 0.4),
    (1, "II", 1.0),
    (2, "III", 2.4),
    (3, "IV", 5.4),
]

_FACTOR_NAMES = {
    "high_risk_surgery": "High-risk surgery",
    "ischemic_heart_disease": "Ischemic heart disease",
    "congestive_heart_failure": "Congestive heart failure",
    "cerebrovascular_disease": "Cerebrovascular disease",
    "insulin_dependent_diabetes": "Insulin-dependent diabetes",
    "preop_creatinine_gt_2": "Preoperative creatinine > 2.0 mg/dL",
}


def compute_rcri(inputs: RCRIInputs) -> RCRIResult:
    factors_present = [name for field, name in _FACTOR_NAMES.items() if getattr(inputs, field)]
    score = len(factors_present)
    # ≥3 factors all map to the same risk class
    score_capped = min(score, 3)
    _, risk_class, risk_pct = _RISK_TABLE[score_capped]
    return RCRIResult(
        score=score,
        risk_class=risk_class,
        estimated_risk_pct=risk_pct,
        factors_present=factors_present,
    )
