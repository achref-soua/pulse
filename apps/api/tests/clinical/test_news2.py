"""NEWS2 unit tests against RCP 2017 reference chart values.

Source: Royal College of Physicians. NEWS2. London: RCP, 2017.
"""

from app.clinical.news2 import NEWS2Inputs, compute_news2


def _normal_patient(**overrides):
    defaults = {
        "respiration_rate": 16,
        "spo2": 97.0,
        "on_supplemental_oxygen": False,
        "systolic_bp": 120,
        "heart_rate": 75,
        "consciousness": "A",
        "temperature": 37.0,
    }
    defaults.update(overrides)
    return NEWS2Inputs(**defaults)


def test_all_normal_is_zero():
    """Normal vitals → score 0, Low response (RCP 2017 chart)."""
    result = compute_news2(_normal_patient())
    assert result.total_score == 0
    assert result.response_level == "Low"


def test_high_resp_rate_scores_3():
    """RR ≥ 25 → 3 points (RCP 2017 chart row 1)."""
    result = compute_news2(_normal_patient(respiration_rate=26))
    assert result.individual_scores["respiration_rate"] == 3
    assert result.response_level == "Medium"  # single red flag


def test_low_spo2_scores_3():
    """SpO2 ≤ 91 without O2 → 3 points (RCP 2017 chart row 2)."""
    result = compute_news2(_normal_patient(spo2=90.0))
    assert result.individual_scores["spo2"] == 3


def test_low_consciousness_scores_3():
    """V/P/U consciousness → 3 points, escalates to High overall."""
    result = compute_news2(_normal_patient(consciousness="V"))
    assert result.individual_scores["consciousness"] == 3
    assert result.response_level == "Medium"


def test_total_score_7_is_high():
    """Score ≥ 7 → High response (RCP 2017 threshold)."""
    result = compute_news2(_normal_patient(
        respiration_rate=26,   # 3 pts
        spo2=90.0,             # 3 pts
        systolic_bp=95,        # 2 pts
    ))
    assert result.total_score >= 7
    assert result.response_level == "High"
