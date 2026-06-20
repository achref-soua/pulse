"""AI Copilot endpoints — streaming chat, patient summary, knowledge listing, PDF report."""

from __future__ import annotations

import json
from collections.abc import AsyncGenerator

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response, StreamingResponse
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.ai.graph import run_summary
from app.ai.prompts import build_system_prompt
from app.ai.report import build_pdf
from app.ai.retriever import all_knowledge, retrieve
from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.database import get_db
from app.models.patient import Patient
from app.models.user import User
from app.schemas.ai import ChatRequest, KBItem, PatientSummaryResponse

log = structlog.get_logger()
router = APIRouter(prefix="/ai", tags=["ai"])


def _require_groq(settings=None):
    s = settings or get_settings()
    if not s.groq_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI features require GROQ_API_KEY — see Settings.",
        )


def _patient_context_str(p: Patient) -> str:
    """Serialize key patient fields into a text block for the system prompt."""
    _COMORBIDITY_LABELS = {
        "htn": "Hypertension", "dm": "Diabetes", "insulin_dependent": "Insulin-dependent DM",
        "ckd": "CKD", "copd": "COPD", "cad": "CAD", "prior_mi": "Prior MI",
        "afib": "AF", "cvd_stroke": "Stroke/CVD", "chf": "CHF",
        "smoking_current": "Current smoker", "smoking_former": "Ex-smoker",
    }
    comorbidities = ", ".join(
        label
        for c in (p.comorbidities or [])
        for field, label in _COMORBIDITY_LABELS.items()
        if getattr(c, field, False)
    )
    meds = ", ".join(m.name for m in (p.medications or []))
    last_vital = (
        sorted(p.vitals or [], key=lambda v: v.taken_at, reverse=True)[:1] or [None]
    )[0]
    vital_str = ""
    if last_vital:
        vital_str = (
            f"Latest vitals: RR={last_vital.rr}, SpO2={last_vital.spo2}%, "
            f"SBP={last_vital.systolic_bp} mmHg, HR={last_vital.heart_rate} bpm, "
            f"Temp={last_vital.temp_c}°C, Consciousness={last_vital.consciousness}"
        )
    return (
        f"Patient: {p.name}, {p.age}y {p.sex}\n"
        f"Diagnosis: {p.aneurysm_type or '—'}, max diameter {p.max_diameter_mm or '—'} mm, "
        f"location {p.location or '—'}\n"
        f"Phase: {p.phase.value}, Planned: {p.planned_intervention.value}\n"
        f"Neck: length {p.neck_length_mm or '—'} mm, angulation {p.neck_angulation_deg or '—'}°, "
        f"diameter {p.neck_diameter_mm or '—'} mm\n"
        f"Iliac access: {p.iliac_access_min_mm or '—'}–{p.iliac_access_max_mm or '—'} mm\n"
        f"Comorbidities: {comorbidities or '—'}\n"
        f"Medications: {meds or '—'}\n"
        f"{vital_str}"
    ).strip()


async def _load_patient(patient_id: str, db: AsyncSession) -> Patient:
    result = await db.execute(
        select(Patient)
        .where(Patient.patient_id == patient_id)
        .options(
            selectinload(Patient.comorbidities),
            selectinload(Patient.medications),
            selectinload(Patient.vitals),
            selectinload(Patient.labs),
        )
    )
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Patient not found")
    return p


# ── GET /ai/knowledge ──────────────────────────────────────────────────────

@router.get("/knowledge", response_model=list[KBItem])
async def list_knowledge(_: User = Depends(get_current_user)):
    """Return all knowledge-base entries (guidelines + literature) without vectors."""
    return all_knowledge()


# ── POST /ai/chat (SSE streaming) ─────────────────────────────────────────

@router.post("/chat")
async def chat_stream(
    req: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Stream a chat response via Server-Sent Events."""
    settings = get_settings()
    _require_groq(settings)

    patient_context = ""
    if req.patient_id:
        try:
            p = await _load_patient(req.patient_id, db)
            patient_context = _patient_context_str(p)
        except HTTPException:
            pass

    async def event_stream() -> AsyncGenerator[str, None]:
        try:
            docs = await retrieve(req.message, top_k=5)
            # Send sources first so the client can render citations immediately
            yield f"data: {json.dumps({'type': 'sources', 'content': docs})}\n\n"

            llm = ChatGroq(
                model=settings.groq_model,
                temperature=settings.groq_temperature,
                api_key=settings.groq_api_key,
                streaming=True,
            )
            system = build_system_prompt(patient_context, docs)
            messages = [SystemMessage(content=system), HumanMessage(content=req.message)]

            async for chunk in llm.astream(messages):
                if chunk.content:
                    yield f"data: {json.dumps({'type': 'token', 'content': chunk.content})}\n\n"

            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        except Exception as exc:
            log.error("ai.chat error", error=str(exc))
            yield f"data: {json.dumps({'type': 'error', 'content': 'AI service error — please retry.'})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ── POST /ai/patient-summary/{patient_id} ─────────────────────────────────

@router.post("/patient-summary/{patient_id}", response_model=PatientSummaryResponse)
async def patient_summary(
    patient_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate a non-streaming AI clinical summary for a patient (LangGraph workflow)."""
    settings = get_settings()
    _require_groq(settings)

    p = await _load_patient(patient_id, db)
    ctx = _patient_context_str(p)
    query = (
        f"Clinical summary for aortic surgery patient: {p.aneurysm_type or 'aortic aneurysm'}, "
        f"{p.age}y, diameter {p.max_diameter_mm or '?'} mm, phase {p.phase.value}"
    )

    summary_text, docs = await run_summary(patient_data=ctx, query=query)

    return PatientSummaryResponse(
        patient_id=patient_id,
        summary=summary_text,
        sources=[
            {
                "id": d["id"],
                "type": d["type"],
                "title": d["title"],
                "body": d["body"],
                "source": d["source"],
                "score": d.get("score"),
            }
            for d in docs
        ],
    )


# ── GET /ai/report/{patient_id} ───────────────────────────────────────────

@router.get("/report/{patient_id}")
async def download_report(
    patient_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate and stream a PDF clinical-summary report."""
    settings = get_settings()
    _require_groq(settings)

    p = await _load_patient(patient_id, db)
    ctx = _patient_context_str(p)
    query = (
        f"Clinical guidelines for {p.aneurysm_type or 'aortic aneurysm'} "
        f"management, phase {p.phase.value}"
    )

    summary_text, docs = await run_summary(patient_data=ctx, query=query)

    # Compute available risk scores from patient labs/vitals inline
    risk_scores: dict = {}
    if p.vitals:
        import dataclasses
        from app.clinical.news2 import NEWS2Inputs, compute_news2
        latest = sorted(p.vitals, key=lambda v: v.taken_at, reverse=True)[0]
        news2_result = compute_news2(NEWS2Inputs(
            respiration_rate=latest.rr or 16,
            spo2=latest.spo2 or 98.0,
            on_supplemental_oxygen=latest.on_oxygen or False,
            systolic_bp=latest.systolic_bp or 120,
            heart_rate=latest.heart_rate or 70,
            consciousness=str(latest.consciousness or "A"),
            temperature=latest.temp_c or 36.5,
        ))
        risk_scores["NEWS2"] = dataclasses.asdict(news2_result)

    patient_dict = {
        "patient_id": p.patient_id,
        "name": p.name,
        "age": p.age,
        "sex": p.sex,
        "aneurysm_type": p.aneurysm_type,
        "phase": p.phase.value,
        "planned_intervention": p.planned_intervention.value,
    }

    pdf_bytes = build_pdf(
        patient=patient_dict,
        summary_text=summary_text,
        risk_scores=risk_scores,
        sources=docs,
    )

    filename = f"pulse-report-{patient_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
