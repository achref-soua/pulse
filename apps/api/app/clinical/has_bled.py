"""HAS-BLED bleeding-risk score.

Reference: Pisters R, et al. Chest. 2010;138(5):1093-1100.
See docs/clinical/REFERENCES.md for full citation.
"""

from dataclasses import dataclass


@dataclass
class HASBLEDInputs:
    hypertension_uncontrolled: bool  # SBP > 160 mmHg — 1 point
    renal_dysfunction: bool  # dialysis, transplant, or creatinine > 200 µmol/L — 1 point
    liver_dysfunction: bool  # cirrhosis or bilirubin >2x + AST/ALT/ALP >3x — 1 point
    stroke_history: bool  # 1 point
    bleeding_predisposition: bool  # bleeding history or predisposition — 1 point
    labile_inr: bool  # TTR < 60% — 1 point
    elderly: bool  # age > 65 — 1 point
    antiplatelet_or_nsaid: bool  # 1 point
    alcohol: bool  # ≥8 drinks/week — 1 point


@dataclass
class HASBLEDResult:
    score: int
    risk_category: str
    annual_bleed_risk_pct: float


# Major bleeding rates per 100 patient-years from original paper (Table 3)
_BLEED_RISK = {0: 1.13, 1: 1.02, 2: 1.88, 3: 3.74, 4: 8.70, 5: 12.50}


def compute_has_bled(inputs: HASBLEDInputs) -> HASBLEDResult:
    score = (
        int(inputs.hypertension_uncontrolled)
        + int(inputs.renal_dysfunction)
        + int(inputs.liver_dysfunction)
        + int(inputs.stroke_history)
        + int(inputs.bleeding_predisposition)
        + int(inputs.labile_inr)
        + int(inputs.elderly)
        + int(inputs.antiplatelet_or_nsaid)
        + int(inputs.alcohol)
    )
    score = min(score, 9)
    risk_pct = _BLEED_RISK.get(min(score, 5), 12.50)

    if score <= 2:
        category = "Low"
    elif score == 3:
        category = "Moderate"
    else:
        category = "High"

    return HASBLEDResult(score=score, risk_category=category, annual_bleed_risk_pct=risk_pct)
