"""RCRI unit tests against Lee et al. 1999 reference values.

Source: Lee TH, et al. Circulation. 1999;100(10):1043-1049 (Table 2).
"""

from app.clinical.rcri import RCRIInputs, compute_rcri


def test_rcri_zero_factors():
    """0 risk factors → Class I, ~0.4% risk (reference: Lee 1999 Table 2)."""
    result = compute_rcri(
        RCRIInputs(
            high_risk_surgery=False,
            ischemic_heart_disease=False,
            congestive_heart_failure=False,
            cerebrovascular_disease=False,
            insulin_dependent_diabetes=False,
            preop_creatinine_gt_2=False,
        )
    )
    assert result.score == 0
    assert result.risk_class == "I"
    assert result.estimated_risk_pct == 0.4
    assert result.factors_present == []


def test_rcri_two_factors():
    """2 risk factors → Class III, ~2.4% risk (reference: Lee 1999 Table 2)."""
    result = compute_rcri(
        RCRIInputs(
            high_risk_surgery=True,
            ischemic_heart_disease=True,
            congestive_heart_failure=False,
            cerebrovascular_disease=False,
            insulin_dependent_diabetes=False,
            preop_creatinine_gt_2=False,
        )
    )
    assert result.score == 2
    assert result.risk_class == "III"
    assert result.estimated_risk_pct == 2.4
    assert len(result.factors_present) == 2


def test_rcri_ge_three_factors():
    """≥3 risk factors → Class IV, ~5.4% risk (reference: Lee 1999 Table 2).
    6 factors still cap at Class IV."""
    result = compute_rcri(
        RCRIInputs(
            high_risk_surgery=True,
            ischemic_heart_disease=True,
            congestive_heart_failure=True,
            cerebrovascular_disease=True,
            insulin_dependent_diabetes=True,
            preop_creatinine_gt_2=True,
        )
    )
    assert result.score == 6
    assert result.risk_class == "IV"
    assert result.estimated_risk_pct == 5.4
    assert len(result.factors_present) == 6
