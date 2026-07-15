"""Pulse MCP server — exposes the clinical tool layer to external AI agents.

Reuses the exact same grounded tools the in-app agent uses (``app.ai.tools``),
so an external agent gets identical, deterministic behaviour: scores come from
the tested calculators, device fit from the IFU engine, cohort facts from
Postgres. Each DB-backed tool opens its own request-scoped session.

Run over stdio:  ``uv run python -m app.mcp``
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from mcp.server.fastmcp import FastMCP

from app.ai import tools as t
from app.core.database import AsyncSessionLocal

mcp = FastMCP(
    "pulse-clinical",
    instructions=(
        "Clinical decision-support tools for aortic and endovascular surgery, over "
        "SYNTHETIC demo data. Scores are computed by deterministic, tested calculators — "
        "never estimate one yourself. Educational use only; not medical advice."
    ),
)


@asynccontextmanager
async def _session():
    """Open a DB session and bind it to the tool layer for the call's duration."""
    async with AsyncSessionLocal() as db:
        t.bind_db(db)
        yield


@mcp.tool()
async def calculate_risk_score(kind: str, inputs: dict) -> dict:
    """Compute a validated clinical risk score (rcri, cha2ds2_vasc, has_bled, news2, gas,
    euroscore2) from explicit inputs. For a real patient, prefer score_patient."""
    return await t.calculate_risk_score.ainvoke({"kind": kind, "inputs": inputs})


@mcp.tool()
async def score_patient(patient_id: str) -> dict:
    """Every applicable score for a patient, inputs derived server-side from the chart."""
    async with _session():
        return await t.score_patient.ainvoke({"patient_id": patient_id})


@mcp.tool()
async def get_patient(patient_id: str) -> dict:
    """A patient's structured record: demographics, aortic anatomy, comorbidities, vitals."""
    async with _session():
        return await t.get_patient.ainvoke({"patient_id": patient_id})


@mcp.tool()
async def match_devices(patient_id: str) -> dict:
    """Rank the stent-graft catalog against a patient's anatomy via the IFU-fit engine."""
    async with _session():
        return await t.match_devices.ainvoke({"patient_id": patient_id})


@mcp.tool()
async def search_guidelines(query: str) -> list[dict]:
    """Semantic search over the clinical guidelines + literature knowledge base."""
    async with _session():
        return await t.search_guidelines.ainvoke({"query": query})


@mcp.tool()
async def query_cohort(filters: dict) -> dict:
    """Count and break down the patient cohort by structured filters (phase,
    planned_intervention, aneurysm_type, sex, min_diameter_mm, min_age, max_age)."""
    async with _session():
        return await t.query_cohort.ainvoke({"filters": filters})


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
