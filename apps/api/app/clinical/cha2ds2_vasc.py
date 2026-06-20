"""CHA₂DS₂-VASc stroke-risk score for atrial fibrillation.

Reference: Lip GY, et al. Chest. 2010;137(2):263-272.
See docs/clinical/REFERENCES.md for full citation.
"""

from dataclasses import dataclass


@dataclass
class CHA2DS2VascInputs:
    congestive_heart_failure: bool   # 1 point
    hypertension: bool               # 1 point
    age_75_or_over: bool             # 2 points
    diabetes_mellitus: bool          # 1 point
    stroke_or_tia: bool              # 2 points — prior stroke/TIA/thromboembolism
    vascular_disease: bool           # 1 point — prior MI, peripheral artery disease, or aortic plaque
    age_65_to_74: bool               # 1 point (mutually exclusive with age_75_or_over)
    female_sex: bool                 # 1 point


@dataclass
class CHA2DS2VascResult:
    score: int
    annual_stroke_risk_pct: float
    recommendation: str


# Annual stroke risk by score (0–9) from the original Chest 2010 paper (Table 4)
_ANNUAL_RISK = {
    0: 0.0,
    1: 1.3,
    2: 2.2,
    3: 3.2,
    4: 4.0,
    5: 6.7,
    6: 9.8,
    7: 9.6,
    8: 6.7,
    9: 15.2,
}


def compute_cha2ds2_vasc(inputs: CHA2DS2VascInputs) -> CHA2DS2VascResult:
    score = (
        int(inputs.congestive_heart_failure)
        + int(inputs.hypertension)
        + (2 if inputs.age_75_or_over else 0)
        + int(inputs.diabetes_mellitus)
        + (2 if inputs.stroke_or_tia else 0)
        + int(inputs.vascular_disease)
        + (1 if inputs.age_65_to_74 and not inputs.age_75_or_over else 0)
        + int(inputs.female_sex)
    )
    score = min(score, 9)
    annual_risk = _ANNUAL_RISK[score]

    if score == 0:
        rec = "Anticoagulation not recommended"
    elif score == 1 and not inputs.female_sex:
        rec = "Consider anticoagulation based on clinical judgment and patient preference"
    else:
        rec = "Oral anticoagulation recommended (unless contraindicated)"

    return CHA2DS2VascResult(score=score, annual_stroke_risk_pct=annual_risk, recommendation=rec)
