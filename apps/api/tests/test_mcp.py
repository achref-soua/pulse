"""Pulse MCP server — tool registration + a grounded call through the MCP layer."""

import pytest

from app.mcp import server


@pytest.mark.asyncio
async def test_mcp_exposes_the_clinical_tools():
    names = {tool.name for tool in await server.mcp.list_tools()}
    assert names == {
        "calculate_risk_score",
        "score_patient",
        "get_patient",
        "match_devices",
        "search_guidelines",
        "query_cohort",
    }


@pytest.mark.asyncio
async def test_mcp_calculate_risk_score_is_grounded():
    # No DB needed — dispatches straight to the tested calculator.
    out = await server.calculate_risk_score(
        kind="rcri",
        inputs={
            "high_risk_surgery": True,
            "ischemic_heart_disease": False,
            "congestive_heart_failure": False,
            "cerebrovascular_disease": False,
            "insulin_dependent_diabetes": False,
            "preop_creatinine_gt_2": False,
        },
    )
    assert out["score"] == 1
    assert out["risk_class"] == "II"
