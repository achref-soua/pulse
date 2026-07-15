"""Deterministic clinical tools exposed to the agent.

The agent NEVER computes a clinical score itself — it calls these grounded
tools. Scoring is delegated to the tested calculators in ``app.clinical.*``;
retrieval to Quiver; cohort/patient/device facts to Postgres. Every tool is a
thin wrapper over code that already exists and is tested elsewhere.

Request-scoped dependencies (the DB session) are passed via a ContextVar set at
the start of each agent turn (``bind_db``) so the tools can stay module-level
``@tool`` functions that the LangGraph ToolNode invokes without threading state.
"""

from __future__ import annotations

from contextvars import ContextVar
from dataclasses import asdict

import structlog
from langchain_core.tools import tool
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.ai.retriever import embed, retrieve
from app.ai.scoring import compute_applicable_scores
from app.clinical.cha2ds2_vasc import CHA2DS2VascInputs, compute_cha2ds2_vasc
from app.clinical.euroscore2 import EuroSCORE2Inputs, compute_euroscore2
from app.clinical.gas import GASInputs, compute_gas
from app.clinical.has_bled import HASBLEDInputs, compute_has_bled
from app.clinical.ifu_fit import DeviceIFU, PatientAnatomy, rank_devices
from app.clinical.news2 import NEWS2Inputs, compute_news2
from app.clinical.rcri import RCRIInputs, compute_rcri
from app.core.quiver_client import COLLECTION_DEVICES, COLLECTION_NOTES, get_quiver_client
from app.models.clinical_note import ClinicalNote
from app.models.device import Device
from app.models.patient import Patient

log = structlog.get_logger()

# ── request-scoped DB session ─────────────────────────────────────────────
_db_ctx: ContextVar[AsyncSession | None] = ContextVar("pulse_agent_db", default=None)


def bind_db(db: AsyncSession) -> None:
    """Bind the current request's DB session for the duration of an agent turn."""
    _db_ctx.set(db)


def _db() -> AsyncSession:
    db = _db_ctx.get()
    if db is None:  # pragma: no cover - guards against calling a tool outside a turn
        raise RuntimeError("agent tools used without a bound DB session — call bind_db() first")
    return db


# ── 1. grounded clinical scores ───────────────────────────────────────────
_CALCULATORS = {
    "rcri": (RCRIInputs, compute_rcri),
    "cha2ds2_vasc": (CHA2DS2VascInputs, compute_cha2ds2_vasc),
    "has_bled": (HASBLEDInputs, compute_has_bled),
    "news2": (NEWS2Inputs, compute_news2),
    "gas": (GASInputs, compute_gas),
    "euroscore2": (EuroSCORE2Inputs, compute_euroscore2),
}


@tool
async def calculate_risk_score(kind: str, inputs: dict) -> dict:
    """Compute a validated clinical risk score with a deterministic, tested calculator.

    Use this for EVERY score — never compute one yourself. ``inputs`` must be read
    from the patient record (use get_patient first), not invented.

    kind: one of rcri, cha2ds2_vasc, has_bled, news2, gas, euroscore2.
    inputs: the calculator's fields, e.g. rcri needs {high_risk_surgery, ischemic_heart_disease,
      congestive_heart_failure, cerebrovascular_disease, insulin_dependent_diabetes,
      preop_creatinine_gt_2} (all booleans); news2 needs {respiration_rate, spo2,
      on_supplemental_oxygen, systolic_bp, heart_rate, consciousness, temperature}.
    Returns the score plus its class/risk fields.
    """
    key = kind.lower().replace("-", "_")
    entry = _CALCULATORS.get(key)
    if entry is None:
        return {"error": f"unknown score '{kind}'. Valid: {', '.join(_CALCULATORS)}"}
    input_cls, compute = entry
    try:
        result = compute(input_cls(**inputs))
    except TypeError as exc:
        return {"error": f"invalid inputs for {key}: {exc}"}
    return asdict(result)


# ── patient serialization ─────────────────────────────────────────────────
async def _load_patient(patient_id: str) -> Patient | None:
    result = await _db().execute(
        select(Patient)
        .where(Patient.patient_id == patient_id)
        .options(
            selectinload(Patient.comorbidities),
            selectinload(Patient.medications),
            selectinload(Patient.vitals),
            selectinload(Patient.labs),
        )
    )
    return result.scalar_one_or_none()


def _patient_dict(p: Patient) -> dict:
    latest = sorted(p.vitals or [], key=lambda v: v.taken_at, reverse=True)[:1]
    v = latest[0] if latest else None
    comorbidities = {
        f: getattr(c, f)
        for c in (p.comorbidities or [])
        for f in ("htn", "dm", "insulin_dependent", "ckd", "copd", "cad", "prior_mi",
                  "afib", "cvd_stroke", "chf", "smoking_current")
        if getattr(c, f, False)
    }
    return {
        "patient_id": p.patient_id,
        "name": p.name,
        "age": p.age,
        "sex": p.sex,
        "aneurysm_type": p.aneurysm_type.value if p.aneurysm_type else None,
        "max_diameter_mm": p.max_diameter_mm,
        "location": p.location,
        "phase": p.phase.value,
        "planned_intervention": p.planned_intervention.value,
        "anatomy": {
            "neck_length_mm": p.neck_length_mm,
            "neck_angulation_deg": p.neck_angulation_deg,
            "neck_diameter_mm": p.neck_diameter_mm,
            "iliac_access_min_mm": p.iliac_access_min_mm,
        },
        "comorbidities": sorted(comorbidities),
        "medications": [m.name for m in (p.medications or [])],
        "latest_vitals": None if v is None else {
            "respiration_rate": v.rr, "spo2": v.spo2, "on_supplemental_oxygen": v.on_oxygen,
            "systolic_bp": v.systolic_bp, "heart_rate": v.heart_rate,
            "temperature": v.temp_c,
            "consciousness": v.consciousness.value if v.consciousness else "A",
        },
    }


# ── 2. structured patient record ──────────────────────────────────────────
@tool
async def score_patient(patient_id: str) -> dict:
    """Compute EVERY applicable clinical score for a real patient, with inputs derived
    server-side from the record (NOT from you). Prefer this over calculate_risk_score
    for any question about a specific patient — it guarantees the inputs match the chart.
    Returns {score_name: result} for each score the record supports (e.g. NEWS2, RCRI, GAS)."""
    p = await _load_patient(patient_id)
    if p is None:
        return {"error": f"patient '{patient_id}' not found"}
    scores = compute_applicable_scores(p)
    if not scores:
        return {"patient_id": patient_id, "scores": {}, "note": "record lacks inputs for any score"}
    return {"patient_id": patient_id, "scores": scores}


@tool
async def get_patient(patient_id: str) -> dict:
    """Fetch a patient's structured clinical record: demographics, aortic anatomy,
    comorbidities, medications and latest vitals. Use this before scoring so you can
    read (not invent) the calculator inputs. patient_id is the short code e.g. 'P-0042'."""
    p = await _load_patient(patient_id)
    if p is None:
        return {"error": f"patient '{patient_id}' not found"}
    return _patient_dict(p)


# ── 3. device fit ranking ─────────────────────────────────────────────────
@tool
async def match_devices(patient_id: str) -> dict:
    """Rank the stent-graft catalog against a patient's aortic anatomy using the
    deterministic IFU-fit engine. Returns each device with an overall suitability
    (suitable / borderline / contraindicated) and per-criterion detail."""
    p = await _load_patient(patient_id)
    if p is None:
        return {"error": f"patient '{patient_id}' not found"}
    required = (p.neck_length_mm, p.neck_angulation_deg, p.neck_diameter_mm,
                p.iliac_access_min_mm, p.max_diameter_mm)
    if any(x is None for x in required):
        return {"error": "patient anatomy incomplete — cannot assess device fit"}

    anatomy = PatientAnatomy(
        max_diameter_mm=p.max_diameter_mm,
        neck_length_mm=p.neck_length_mm,
        neck_angulation_deg=p.neck_angulation_deg,
        neck_diameter_mm=p.neck_diameter_mm,
        iliac_access_min_mm=p.iliac_access_min_mm,
    )
    rows = (await _db().execute(select(Device))).scalars().all()
    devices = [
        DeviceIFU(
            name=f"{d.manufacturer} {d.name}",
            ifu_min_neck_length_mm=d.ifu_min_neck_length_mm,
            ifu_max_neck_angulation_deg=d.ifu_max_neck_angulation_deg,
            ifu_proximal_min_mm=d.ifu_proximal_min_mm,
            ifu_proximal_max_mm=d.ifu_proximal_max_mm,
            ifu_iliac_min_mm=d.ifu_iliac_min_mm,
            ifu_iliac_max_mm=d.ifu_iliac_max_mm,
            ifu_distal_min_mm=d.ifu_distal_min_mm,
            ifu_distal_max_mm=d.ifu_distal_max_mm,
        )
        for d in rows
    ]
    if not devices:
        return {"patient_id": patient_id, "devices": []}
    ranked = [asdict(r) for r in rank_devices(anatomy, devices)]
    return {"patient_id": patient_id, "devices": ranked}


# ── 4. guideline / literature retrieval ───────────────────────────────────
@tool
async def search_guidelines(query: str) -> list[dict]:
    """Semantic search over the clinical guidelines + literature knowledge base.
    Use this to ground clinical statements. Returns ranked passages with title,
    body and citable source. Cite results by their source when you use them."""
    docs = await retrieve(query, top_k=5)
    return [
        {"title": d["title"], "type": d["type"], "body": d["body"], "source": d["source"]}
        for d in docs
    ]


# ── 5. device catalog search + lookup ─────────────────────────────────────
async def _search_collection(collection: str, query: str, k: int) -> list:
    try:
        vec = await embed(query)
        async with get_quiver_client() as q:
            return await q.search(collection, vec, k=k)
    except Exception as exc:  # graceful degrade — vector store is optional
        log.warning("tool.vector_search failed", collection=collection, error=str(exc))
        return []


@tool
async def search_device_catalog(query: str) -> list[dict]:
    """Semantic search over the stent-graft device catalog (e.g. 'low-profile TEVAR
    for tight iliacs'). Returns matching devices with manufacturer, indication and
    IFU envelope. For a full IFU on one device use get_device."""
    hits = await _search_collection(COLLECTION_DEVICES, query, k=5)
    names = [h.payload.get("name") for h in hits if getattr(h, "payload", None)]
    if not names:
        return []
    rows = (await _db().execute(select(Device).where(Device.name.in_(names)))).scalars().all()
    by_name = {d.name: d for d in rows}
    out = []
    for name in names:  # preserve vector-rank order
        d = by_name.get(name)
        if d:
            out.append(_device_dict(d))
    return out


@tool
async def get_device(name: str) -> dict:
    """Fetch a single stent-graft device's full IFU envelope by (partial) name."""
    d = (
        await _db().execute(select(Device).where(Device.name.ilike(f"%{name}%")).limit(1))
    ).scalar_one_or_none()
    if d is None:
        return {"error": f"device '{name}' not found"}
    return _device_dict(d)


def _device_dict(d: Device) -> dict:
    return {
        "name": d.name,
        "manufacturer": d.manufacturer,
        "indication": d.indication,
        "ifu": {
            "neck_length_min_mm": d.ifu_min_neck_length_mm,
            "neck_angulation_max_deg": d.ifu_max_neck_angulation_deg,
            "proximal_mm": [d.ifu_proximal_min_mm, d.ifu_proximal_max_mm],
            "distal_mm": [d.ifu_distal_min_mm, d.ifu_distal_max_mm],
            "iliac_mm": [d.ifu_iliac_min_mm, d.ifu_iliac_max_mm],
            "sheath_fr": d.sheath_fr,
        },
    }


# ── 6. cohort aggregates ──────────────────────────────────────────────────
@tool
async def query_cohort(filters: dict | None = None) -> dict:
    """Count and break down the patient cohort by structured filters. Supported keys
    (all optional): phase, planned_intervention, aneurysm_type, sex ('M'/'F'),
    min_diameter_mm, min_age, max_age. Omit filters (or pass {}) to count the whole cohort.
    Returns the matching total plus breakdowns by phase and planned intervention.
    Use for questions like 'how many pre-op EVAR patients'."""
    filters = filters or {}
    conds = []
    if v := filters.get("phase"):
        conds.append(Patient.phase == v)
    if v := filters.get("planned_intervention"):
        conds.append(Patient.planned_intervention == v)
    if v := filters.get("aneurysm_type"):
        conds.append(Patient.aneurysm_type == v)
    if v := filters.get("sex"):
        conds.append(Patient.sex == v)
    if (v := filters.get("min_diameter_mm")) is not None:
        conds.append(Patient.max_diameter_mm >= v)
    if (v := filters.get("min_age")) is not None:
        conds.append(Patient.age >= v)
    if (v := filters.get("max_age")) is not None:
        conds.append(Patient.age <= v)

    db = _db()
    total = (await db.execute(select(func.count()).select_from(Patient).where(*conds))).scalar_one()
    by_phase = (
        await db.execute(
            select(Patient.phase, func.count()).where(*conds).group_by(Patient.phase)
        )
    ).all()
    by_intervention = (
        await db.execute(
            select(Patient.planned_intervention, func.count())
            .where(*conds)
            .group_by(Patient.planned_intervention)
        )
    ).all()
    return {
        "total": total,
        "by_phase": {p.value: n for p, n in by_phase},
        "by_intervention": {i.value: n for i, n in by_intervention},
    }


# ── 7. patient notes search ───────────────────────────────────────────────
@tool
async def search_patient_notes(query: str, patient_id: str | None = None) -> list[dict]:
    """Semantic search over clinical notes (operative, progress, consult). Optionally
    scope to one patient_id. Returns note snippets with type, author role and date."""
    hits = await _search_collection(COLLECTION_NOTES, query, k=8)
    pids = [h.payload.get("patient_id") for h in hits if getattr(h, "payload", None)]
    if patient_id:
        pids = [pid for pid in pids if pid == patient_id]
    if not pids:
        return []
    rows = (
        await _db().execute(
            select(ClinicalNote, Patient.patient_id)
            .join(Patient, ClinicalNote.patient_id == Patient.id)
            .where(Patient.patient_id.in_(pids))
            .order_by(ClinicalNote.timestamp.desc())
            .limit(8)
        )
    ).all()
    return [
        {
            "patient_id": pid,
            "note_type": note.note_type.value,
            "author_role": note.author_role,
            "date": note.timestamp.date().isoformat(),
            "body": note.body,
        }
        for note, pid in rows
    ]


TOOLS = [
    calculate_risk_score,
    score_patient,
    get_patient,
    match_devices,
    search_guidelines,
    search_device_catalog,
    get_device,
    query_cohort,
    search_patient_notes,
]
