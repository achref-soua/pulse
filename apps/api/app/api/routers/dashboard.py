from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_role
from app.core.database import get_db
from app.models.patient import Patient, Phase, PlannedIntervention
from app.models.user import User, UserRole
from app.models.vital import Vital
from app.schemas.dashboard import DashboardStats, PhaseBreakdown

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

_CLINICAL_ROLES = (UserRole.surgeon, UserRole.anesthetist, UserRole.nurse, UserRole.admin)


async def _news2_high_count(db: AsyncSession) -> int:
    """Count post-phase patients whose most-recent vitals suggest a high NEWS2 score.

    High NEWS2 (≥7) is approximated by single-parameter red flags:
    RR ≥ 25, SpO2 ≤ 91, systolic BP ≤ 90, HR ≥ 131, or temp ≤ 35.0.
    This is a database-level proxy; exact scoring uses the clinical engine.
    """
    latest_vital_ids = (
        select(func.max(Vital.id).label("vid"))
        .join(Patient, Patient.id == Vital.patient_id)
        .where(Patient.phase == Phase.post)
        .group_by(Vital.patient_id)
        .scalar_subquery()
    )
    result = await db.execute(
        select(func.count())
        .select_from(Vital)
        .where(
            and_(
                Vital.id.in_(latest_vital_ids),
                (
                    (Vital.rr >= 25)
                    | (Vital.spo2 <= 91)
                    | (Vital.systolic_bp <= 90)
                    | (Vital.heart_rate >= 131)
                    | (Vital.temp_c <= 35.0)
                ),
            )
        )
    )
    return result.scalar_one()


@router.get("/stats", response_model=DashboardStats)
async def dashboard_stats(
    _: User = Depends(require_role(*_CLINICAL_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> DashboardStats:
    total = (await db.execute(select(func.count()).select_from(Patient))).scalar_one()

    phase_rows = (await db.execute(select(Patient.phase, func.count()).group_by(Patient.phase))).all()
    phase_map: dict[str, int] = {row[0]: row[1] for row in phase_rows}

    upcoming_date = date.today() + timedelta(days=7)
    upcoming = (
        await db.execute(
            select(func.count())
            .select_from(Patient)
            .where(
                and_(
                    Patient.surgery_date.isnot(None),
                    Patient.surgery_date <= upcoming_date,
                    Patient.surgery_date >= date.today(),
                    Patient.planned_intervention != PlannedIntervention.surveillance,
                )
            )
        )
    ).scalar_one()

    # Borderline anatomy proxy: neck angulation 50–75° or neck length 5–14 mm
    borderline = (
        await db.execute(
            select(func.count())
            .select_from(Patient)
            .where((Patient.neck_angulation_deg.between(50, 75)) | (Patient.neck_length_mm.between(5, 14)))
        )
    ).scalar_one()

    # Challenging anatomy proxy: neck angulation > 75° or neck length < 5 mm
    challenging = (
        await db.execute(
            select(func.count())
            .select_from(Patient)
            .where((Patient.neck_angulation_deg > 75) | (Patient.neck_length_mm < 5))
        )
    ).scalar_one()

    high_news2 = await _news2_high_count(db)

    return DashboardStats(
        total_patients=total,
        by_phase=PhaseBreakdown(
            pre=phase_map.get("pre", 0),
            intra=phase_map.get("intra", 0),
            post=phase_map.get("post", 0),
        ),
        high_news2_count=high_news2,
        borderline_anatomy_count=borderline,
        challenging_anatomy_count=challenging,
        upcoming_procedures=upcoming,
    )
