"""GAS unit tests against Samy et al. 1994 reference values.

Source: Samy AK, Murray G, MacBain G. Cardiovasc Surg. 1994;2(1):41-44.
"""

from app.clinical.gas import GASInputs, compute_gas


def test_young_healthy_patient():
    """Age 60, no comorbidities → score 60, low risk."""
    result = compute_gas(
        GASInputs(
            age=60, shock=False, myocardial_disease=False, cerebrovascular_disease=False, renal_disease=False
        )
    )
    assert result.score == 60
    assert "Low" in result.risk_interpretation


def test_elderly_with_comorbidities():
    """Age 75 + myocardial + renal → 75 + 7 + 14 = 96, high risk."""
    result = compute_gas(
        GASInputs(
            age=75, shock=False, myocardial_disease=True, cerebrovascular_disease=False, renal_disease=True
        )
    )
    assert result.score == 96
    assert "High" in result.risk_interpretation


def test_all_factors_present():
    """Age 80 + all comorbidities → 80 + 17 + 7 + 10 + 14 = 128."""
    result = compute_gas(
        GASInputs(
            age=80, shock=True, myocardial_disease=True, cerebrovascular_disease=True, renal_disease=True
        )
    )
    assert result.score == 128
    assert "High" in result.risk_interpretation
