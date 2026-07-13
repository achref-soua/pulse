"""Cohort analytics — Postgres aggregate distributions for the /analytics dashboard."""

from fastapi import APIRouter, Depends
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_role
from app.core.database import get_db
from app.models.patient import Patient
from app.models.user import User, UserRole

router = APIRouter(prefix="/analytics", tags=["analytics"])

_CLINICAL_ROLES = (UserRole.surgeon, UserRole.anesthetist, UserRole.nurse, UserRole.admin)


async def _counts_by(db: AsyncSession, column) -> dict[str, int]:
    rows = (await db.execute(select(column, func.count()).group_by(column))).all()
    return {(v.value if hasattr(v, "value") else str(v)): n for v, n in rows}


@router.get("/overview")
async def analytics_overview(
    _: User = Depends(require_role(*_CLINICAL_ROLES)),
    db: AsyncSession = Depends(get_db),
):
    """Return cohort distributions (phase, intervention, aneurysm type, sex, age bands,
    max-diameter bands) in a single payload for the analytics dashboard."""
    total = (await db.execute(select(func.count()).select_from(Patient))).scalar_one()

    # Diameter bands keyed to AAA surveillance/repair thresholds.
    diameter_band = case(
        (Patient.max_diameter_mm < 50, "<50"),
        (Patient.max_diameter_mm < 55, "50–55"),
        (Patient.max_diameter_mm < 60, "55–60"),
        else_="≥60",
    )
    age_band = case(
        (Patient.age < 60, "<60"),
        (Patient.age < 70, "60–69"),
        (Patient.age < 80, "70–79"),
        else_="≥80",
    )
    diameter_rows = (
        await db.execute(
            select(diameter_band, func.count())
            .where(Patient.max_diameter_mm.isnot(None))
            .group_by(diameter_band)
        )
    ).all()
    age_rows = (await db.execute(select(age_band, func.count()).group_by(age_band))).all()

    return {
        "total": total,
        "by_phase": await _counts_by(db, Patient.phase),
        "by_intervention": await _counts_by(db, Patient.planned_intervention),
        "by_aneurysm_type": await _counts_by(db, Patient.aneurysm_type),
        "by_sex": await _counts_by(db, Patient.sex),
        "by_age_band": dict(age_rows),
        "by_diameter_band": dict(diameter_rows),
    }
