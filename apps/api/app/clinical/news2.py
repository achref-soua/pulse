"""NEWS2 — National Early Warning Score 2.

Reference: Royal College of Physicians. NEWS2. London: RCP, 2017.
https://www.rcplondon.ac.uk/projects/outputs/national-early-warning-score-news-2
See docs/clinical/REFERENCES.md for full citation.
"""

from dataclasses import dataclass


@dataclass
class NEWS2Inputs:
    respiration_rate: int  # breaths per minute
    spo2: float  # SpO2 percentage
    on_supplemental_oxygen: bool
    systolic_bp: int  # mmHg
    heart_rate: int  # bpm
    consciousness: str  # "A" = Alert, "V/P/U" = any other → score 3
    temperature: float  # Celsius


@dataclass
class NEWS2Result:
    total_score: int
    response_level: str  # Low / Medium / High
    individual_scores: dict[str, int]


def _rr_score(rr: int) -> int:
    if rr <= 8:
        return 3
    if rr <= 11:
        return 1
    if rr <= 20:
        return 0
    if rr <= 24:
        return 2
    return 3


def _spo2_score(spo2: float, on_o2: bool) -> int:
    # Scale 1 (hypercapnic risk patients use Scale 2 — not implemented here)
    if spo2 <= 91:
        return 3
    if spo2 <= 93:
        return 2
    if spo2 <= 94:
        return 1
    if on_o2:
        return 2
    return 0


def _sbp_score(sbp: int) -> int:
    if sbp <= 90:
        return 3
    if sbp <= 100:
        return 2
    if sbp <= 110:
        return 1
    if sbp <= 219:
        return 0
    return 3


def _hr_score(hr: int) -> int:
    if hr <= 40:
        return 3
    if hr <= 50:
        return 1
    if hr <= 90:
        return 0
    if hr <= 110:
        return 1
    if hr <= 130:
        return 2
    return 3


def _temp_score(temp: float) -> int:
    if temp <= 35.0:
        return 3
    if temp <= 36.0:
        return 1
    if temp <= 38.0:
        return 0
    if temp <= 39.0:
        return 1
    return 2


def compute_news2(inputs: NEWS2Inputs) -> NEWS2Result:
    consciousness_score = 0 if inputs.consciousness == "A" else 3

    individual = {
        "respiration_rate": _rr_score(inputs.respiration_rate),
        "spo2": _spo2_score(inputs.spo2, inputs.on_supplemental_oxygen),
        "systolic_bp": _sbp_score(inputs.systolic_bp),
        "heart_rate": _hr_score(inputs.heart_rate),
        "consciousness": consciousness_score,
        "temperature": _temp_score(inputs.temperature),
    }
    total = sum(individual.values())

    # Any single parameter scoring 3 → Medium at minimum
    has_red_flag = any(v == 3 for v in individual.values())

    if total >= 7:
        level = "High"
    elif total >= 5 or has_red_flag:
        level = "Medium"
    else:
        level = "Low"

    return NEWS2Result(total_score=total, response_level=level, individual_scores=individual)
