"""AI Copilot endpoints — streaming chat, patient summary, knowledge listing, PDF report."""

from __future__ import annotations

import json
import uuid
from collections.abc import AsyncGenerator

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response, StreamingResponse
from langchain_core.messages import AIMessage, HumanMessage
from langchain_groq import ChatGroq
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.ai import tools as agent_tools
from app.ai.graph import run_agent_events, run_summary
from app.ai.report import build_pdf
from app.ai.retriever import all_knowledge
from app.ai.scoring import compute_applicable_scores, scores_as_text
from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.database import get_db
from app.models.conversation import Conversation, Message
from app.models.patient import Patient
from app.models.user import User
from app.schemas.ai import (
    ChatRequest,
    CohortFilters,
    KBItem,
    NLCohortRequest,
    NLCohortResponse,
    PatientSummaryResponse,
)

log = structlog.get_logger()
router = APIRouter(prefix="/ai", tags=["ai"])

_COMORBIDITY_LABELS = {
    "htn": "Hypertension", "dm": "Diabetes", "insulin_dependent": "Insulin-dependent DM",
    "ckd": "CKD", "copd": "COPD", "cad": "CAD", "prior_mi": "Prior MI",
    "afib": "AF", "cvd_stroke": "Stroke/CVD", "chf": "CHF",
    "smoking_current": "Current smoker", "smoking_former": "Ex-smoker",
}


def _require_groq(settings=None):
    s = settings or get_settings()
    if not s.groq_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI features require GROQ_API_KEY — see Settings.",
        )


def _patient_context_str(p: Patient) -> str:
    """Serialize key patient fields into a text block for the system prompt."""
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

def _sse(event: dict) -> str:
    return f"data: {json.dumps(event)}\n\n"


async def _load_thread(thread_id: str | None, user_id: uuid.UUID, db: AsyncSession):
    """Return (conversation, prior LangChain messages) for a thread the user owns."""
    if not thread_id:
        return None, []
    try:
        cid = uuid.UUID(thread_id)
    except ValueError:
        return None, []
    conv = (
        await db.execute(
            select(Conversation)
            .where(Conversation.id == cid, Conversation.user_id == user_id)
            .options(selectinload(Conversation.messages))
        )
    ).scalar_one_or_none()
    if conv is None:
        return None, []
    history = [
        HumanMessage(content=m.content) if m.role == "user" else AIMessage(content=m.content)
        for m in conv.messages
    ]
    return conv, history


@router.post("/chat")
async def chat_stream(
    req: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Stream the agent's reasoning over SSE: router → tool_call/tool_result → sources → token."""
    settings = get_settings()
    _require_groq(settings)

    patient_context = ""
    if req.patient_id:
        try:
            p = await _load_patient(req.patient_id, db)
            patient_context = _patient_context_str(p)
        except HTTPException:
            pass

    conv, history = await _load_thread(req.thread_id, current_user.id, db)
    if conv is None:
        conv = Conversation(user_id=current_user.id, title=req.message[:200])
        db.add(conv)
        await db.flush()
    thread_id = str(conv.id)
    messages = [*history, HumanMessage(content=req.message)]
    agent_tools.bind_db(db)  # request-scoped session for the tools

    async def event_stream() -> AsyncGenerator[str, None]:
        answer = ""
        try:
            yield _sse({"type": "thread", "content": thread_id})
            async for ev in run_agent_events(messages, patient_context):
                if ev["type"] == "done":
                    answer = ev.get("content", "")
                yield _sse(ev)
        except Exception as exc:
            log.error("ai.chat error", error=str(exc))
            yield _sse({"type": "error", "content": "AI service error — please retry."})
            return

        # Persist the turn for multi-turn memory (best-effort — never breaks the stream).
        try:
            db.add(Message(conversation_id=conv.id, role="user", content=req.message))
            if answer:
                db.add(Message(conversation_id=conv.id, role="assistant", content=answer))
            await db.commit()
        except Exception as exc:
            log.warning("ai.chat persist failed", error=str(exc))

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ── POST /ai/nl-cohort ─────────────────────────────────────────────────────

_NL_COHORT_PROMPT = """Extract structured patient-roster filters from the query below. \
Return ONLY a JSON object with any of these keys that apply (omit the rest):
- phase: one of "pre", "intra", "post"
- planned_intervention: one of "EVAR", "TEVAR", "open_graft", "surveillance"
- aneurysm_type: one of "infrarenal_AAA", "juxtarenal_AAA", "TAA", "ascending"
- sex: "M" or "F"
- min_diameter_mm: number (for "large"/"big" aneurysms use 55)
- min_age, max_age: integers ("elderly" → min_age 75)
Return {{}} if nothing maps. No prose.

Query: {query}"""


@router.post("/nl-cohort", response_model=NLCohortResponse)
async def nl_cohort(
    req: NLCohortRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Turn a natural-language cohort description into structured filters + matching patients."""
    settings = get_settings()
    _require_groq(settings)

    llm = ChatGroq(
        model=settings.groq_router_model,  # extraction is simple — the fast 8B is enough
        temperature=0,
        api_key=settings.groq_api_key,
        model_kwargs={"response_format": {"type": "json_object"}},
    )
    try:
        reply = await llm.ainvoke([HumanMessage(content=_NL_COHORT_PROMPT.format(query=req.query))])
        raw = json.loads(reply.content)
    except Exception as exc:  # extraction is best-effort — degrade to empty filters
        log.warning("nl_cohort extraction failed", error=str(exc))
        raw = {}

    # Validate/coerce through the schema so a hallucinated key can't reach the query.
    filters = CohortFilters(**{k: v for k, v in raw.items() if k in CohortFilters.model_fields})

    conds = []
    if filters.phase:
        conds.append(Patient.phase == filters.phase)
    if filters.planned_intervention:
        conds.append(Patient.planned_intervention == filters.planned_intervention)
    if filters.aneurysm_type:
        conds.append(Patient.aneurysm_type == filters.aneurysm_type)
    if filters.sex:
        conds.append(Patient.sex == filters.sex)
    if filters.min_diameter_mm is not None:
        conds.append(Patient.max_diameter_mm >= filters.min_diameter_mm)
    if filters.min_age is not None:
        conds.append(Patient.age >= filters.min_age)
    if filters.max_age is not None:
        conds.append(Patient.age <= filters.max_age)

    # Fail closed: if nothing mapped (extraction error or an unmappable query), return an
    # empty cohort rather than silently matching every patient with an unfiltered query.
    if not conds:
        return NLCohortResponse(query=req.query, filters=filters, total=0, patient_ids=[])

    rows = (
        await db.execute(
            select(Patient.patient_id).where(*conds).order_by(Patient.patient_id).limit(500)
        )
    ).scalars().all()
    return NLCohortResponse(query=req.query, filters=filters, total=len(rows), patient_ids=list(rows))


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

    scores = compute_applicable_scores(p)
    summary_text, docs = await run_summary(
        patient_data=ctx, query=query, scores_text=scores_as_text(scores)
    )

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

    # Compute every applicable score deterministically, then narrate grounded in them.
    risk_scores = compute_applicable_scores(p)
    summary_text, docs = await run_summary(
        patient_data=ctx, query=query, scores_text=scores_as_text(risk_scores)
    )

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
