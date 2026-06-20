from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, require_role
from app.core.database import get_db
from app.models.audit_log import AuditLog
from app.models.patient import Patient, Phase, PlannedIntervention
from app.models.user import User, UserRole
from app.schemas.patient import PatientListItem, PatientResponse

router = APIRouter(prefix="/patients", tags=["patients"])

_CLINICAL_ROLES = (UserRole.surgeon, UserRole.anesthetist, UserRole.nurse, UserRole.admin)


@router.get("", response_model=list[PatientListItem])
async def list_patients(
    request: Request,
    phase: Phase | None = Query(None),
    intervention: PlannedIntervention | None = Query(None),
    search: str | None = Query(None, max_length=100),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_role(*_CLINICAL_ROLES)),
    db: AsyncSession = Depends(get_db),
):
    q = select(Patient)
    if phase:
        q = q.where(Patient.phase == phase)
    if intervention:
        q = q.where(Patient.planned_intervention == intervention)
    if search:
        q = q.where(Patient.name.ilike(f"%{search}%") | Patient.patient_id.ilike(f"%{search}%"))
    q = q.order_by(Patient.patient_id).limit(limit).offset(offset)

    result = await db.execute(q)
    patients = result.scalars().all()

    db.add(
        AuditLog(
            user_id=current_user.id,
            action="list",
            entity="patient",
            entity_id=f"count={len(patients)} filters=phase:{phase},intervention:{intervention}",
            ip_address=request.client.host if request.client else None,
        )
    )

    return patients


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Patient)
        .where(Patient.patient_id == patient_id)
        .options(
            selectinload(Patient.comorbidities),
            selectinload(Patient.labs),
            selectinload(Patient.medications),
            selectinload(Patient.vitals),
            selectinload(Patient.clinical_notes),
        )
    )
    patient = result.scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    log = AuditLog(
        user_id=current_user.id,
        action="read",
        entity="patient",
        entity_id=patient_id,
        ip_address=request.client.host if request.client else None,
    )
    db.add(log)

    return patient
