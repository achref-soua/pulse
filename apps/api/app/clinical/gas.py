"""Glasgow Aneurysm Score (GAS) — AAA operative risk.

Reference: Samy AK, Murray G, MacBain G. Cardiovasc Surg. 1994;2(1):41-44.
See docs/clinical/REFERENCES.md for full citation.
"""

from dataclasses import dataclass


@dataclass
class GASInputs:
    age: int
    shock: bool  # systolic BP < 90 mmHg on admission
    myocardial_disease: bool  # history of MI, CCF, or angina
    cerebrovascular_disease: bool
    renal_disease: bool  # any history of renal impairment


@dataclass
class GASResult:
    score: float
    risk_interpretation: str


def compute_gas(inputs: GASInputs) -> GASResult:
    score = (
        inputs.age
        + (17 * int(inputs.shock))
        + (7 * int(inputs.myocardial_disease))
        + (10 * int(inputs.cerebrovascular_disease))
        + (14 * int(inputs.renal_disease))
    )

    if score < 77:
        interpretation = "Low operative risk"
    elif score < 91:
        interpretation = "Moderate operative risk"
    else:
        interpretation = "High operative risk — consider EVAR or conservative management"

    return GASResult(score=score, risk_interpretation=interpretation)
