"""EuroSCORE II — cardiac surgery operative risk.

Reference: Nashef SA, et al. Eur J Cardiothorac Surg. 2012;41(4):734-745.
Official calculator: https://www.euroscore.org/calc.html

NOTE: This implementation uses the published logistic-regression coefficients
from the 2012 paper. Results are labeled "educational estimate" because the
official calculator applies additional institutional calibration factors.
Validate against the official calculator before any clinical reference.
"""

import math
from dataclasses import dataclass


@dataclass
class EuroSCORE2Inputs:
    age: int
    female: bool
    renal_dysfunction: str  # "none" | "moderate" | "dialysis"
    extracardiac_arteriopathy: bool
    poor_mobility: bool
    previous_cardiac_surgery: bool
    chronic_lung_disease: bool
    active_endocarditis: bool
    critical_preop_state: bool
    diabetes_on_insulin: bool
    nyha_class: int  # 1 | 2 | 3 | 4
    ccs_angina: int  # 0 = no angina, 1–4 = CCS class
    ejection_fraction_pct: float
    recent_mi: bool  # MI within 90 days
    pulmonary_hypertension: str  # "none" | "moderate" | "severe"
    emergency: bool
    other_than_isolated_cabg: bool
    thoracic_aorta_surgery: bool


@dataclass
class EuroSCORE2Result:
    predicted_mortality_pct: float
    risk_category: str
    note: str = (
        "Educational estimate using published EuroSCORE II logistic "
        "coefficients (Nashef et al. 2012). Validate with the official "
        "calculator at euroscore.org before any clinical reference."
    )


# Published coefficients from Nashef et al. 2012, Table 3
# Intercept: -5.324537
_INTERCEPT = -5.324537

_COEFFICIENTS: dict[str, float] = {
    "age_gt_60": 0.0285181,  # per year above 60
    "female": 0.2196434,
    "renal_moderate": 0.303553,  # eGFR 50–85
    "renal_dialysis": 0.9058694,
    "extracardiac_arteriopathy": 0.5360268,
    "poor_mobility": 0.2196434,
    "previous_cardiac_surgery": 1.118599,
    "chronic_lung_disease": 0.1886564,
    "active_endocarditis": 0.6420417,
    "critical_preop_state": 1.086517,
    "diabetes_on_insulin": 0.3542749,
    "nyha_2": 0.1070545,
    "nyha_3": 0.2958358,
    "nyha_4": 0.5597929,
    "ccs_4_angina": 0.2226147,
    "ef_30_to_50": 0.4191643,
    "ef_lt_30": 1.094443,
    "recent_mi": 0.1731475,
    "pulmonary_htn_moderate": 0.1788899,
    "pulmonary_htn_severe": 0.3491475,
    "emergency": 0.9058694,
    "other_than_isolated_cabg": 0.0062118,
    "thoracic_aorta": 0.6527205,
}


def compute_euroscore2(inputs: EuroSCORE2Inputs) -> EuroSCORE2Result:
    log_odds = _INTERCEPT

    age_excess = max(0, inputs.age - 60)
    log_odds += _COEFFICIENTS["age_gt_60"] * age_excess

    if inputs.female:
        log_odds += _COEFFICIENTS["female"]
    if inputs.renal_dysfunction == "moderate":
        log_odds += _COEFFICIENTS["renal_moderate"]
    elif inputs.renal_dysfunction == "dialysis":
        log_odds += _COEFFICIENTS["renal_dialysis"]
    if inputs.extracardiac_arteriopathy:
        log_odds += _COEFFICIENTS["extracardiac_arteriopathy"]
    if inputs.poor_mobility:
        log_odds += _COEFFICIENTS["poor_mobility"]
    if inputs.previous_cardiac_surgery:
        log_odds += _COEFFICIENTS["previous_cardiac_surgery"]
    if inputs.chronic_lung_disease:
        log_odds += _COEFFICIENTS["chronic_lung_disease"]
    if inputs.active_endocarditis:
        log_odds += _COEFFICIENTS["active_endocarditis"]
    if inputs.critical_preop_state:
        log_odds += _COEFFICIENTS["critical_preop_state"]
    if inputs.diabetes_on_insulin:
        log_odds += _COEFFICIENTS["diabetes_on_insulin"]

    nyha_key = {2: "nyha_2", 3: "nyha_3", 4: "nyha_4"}.get(inputs.nyha_class)
    if nyha_key:
        log_odds += _COEFFICIENTS[nyha_key]

    if inputs.ccs_angina == 4:
        log_odds += _COEFFICIENTS["ccs_4_angina"]

    if inputs.ejection_fraction_pct < 30:
        log_odds += _COEFFICIENTS["ef_lt_30"]
    elif inputs.ejection_fraction_pct < 50:
        log_odds += _COEFFICIENTS["ef_30_to_50"]

    if inputs.recent_mi:
        log_odds += _COEFFICIENTS["recent_mi"]

    if inputs.pulmonary_hypertension == "moderate":
        log_odds += _COEFFICIENTS["pulmonary_htn_moderate"]
    elif inputs.pulmonary_hypertension == "severe":
        log_odds += _COEFFICIENTS["pulmonary_htn_severe"]

    if inputs.emergency:
        log_odds += _COEFFICIENTS["emergency"]
    if inputs.other_than_isolated_cabg:
        log_odds += _COEFFICIENTS["other_than_isolated_cabg"]
    if inputs.thoracic_aorta_surgery:
        log_odds += _COEFFICIENTS["thoracic_aorta"]

    prob = 1 / (1 + math.exp(-log_odds)) * 100

    if prob < 2:
        category = "Low risk"
    elif prob < 5:
        category = "Moderate risk"
    elif prob < 10:
        category = "High risk"
    else:
        category = "Very high risk"

    return EuroSCORE2Result(predicted_mortality_pct=round(prob, 2), risk_category=category)
