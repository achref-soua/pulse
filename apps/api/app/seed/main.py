"""Idempotent seed script — populates Postgres and Quiver with synthetic demo data."""

import asyncio
import logging
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings
from app.core.quiver_client import (
    COLLECTION_DEVICES,
    COLLECTION_GUIDELINES,
    COLLECTION_LITERATURE,
    COLLECTION_NOTES,
    ensure_collections,
    get_quiver_client,
)
from app.core.security import hash_password
from app.models import *  # noqa: F401, F403 — register all models
from app.models.clinical_note import ClinicalNote, NoteType
from app.models.comorbidity import Comorbidity
from app.models.device import Device
from app.models.lab import Lab
from app.models.medication import MedClass, Medication
from app.models.patient import AneurysmType, Patient, Phase, PlannedIntervention
from app.models.user import User, UserRole
from app.models.vital import AVPU, Vital
from app.seed.generators import (
    DEVICE_CATALOG,
    GUIDELINES_CORPUS,
    LITERATURE_CORPUS,
    generate_patients,
)

log = logging.getLogger(__name__)

DEMO_USERS = [
    {
        "email": "surgeon@demo.pulse",
        "password": "demo-surgeon-2024",
        "full_name": "Dr. Alex Harrington",
        "role": UserRole.surgeon,
    },
    {
        "email": "anesthetist@demo.pulse",
        "password": "demo-anesthetist-2024",
        "full_name": "Dr. Priya Mehta",
        "role": UserRole.anesthetist,
    },
    {
        "email": "nurse@demo.pulse",
        "password": "demo-nurse-2024",
        "full_name": "Sam Taylor",
        "role": UserRole.nurse,
    },
    {
        "email": "admin@demo.pulse",
        "password": "demo-admin-2024",
        "full_name": "Jordan Lee",
        "role": UserRole.admin,
    },
]

_MED_CLASS_MAP: dict[str, MedClass] = {
    "antiplatelet": MedClass.antiplatelet,
    "anticoagulant": MedClass.anticoagulant,
    "statin": MedClass.statin,
    "beta_blocker": MedClass.beta_blocker,
    "ACEi/ARB": MedClass.acei_arb,
    "diuretic": MedClass.diuretic,
}

_ANEURYSM_TYPE_MAP: dict[str, AneurysmType] = {
    "infrarenal_AAA": AneurysmType.infrarenal_aaa,
    "juxtarenal_AAA": AneurysmType.juxtarenal_aaa,
    "TAA": AneurysmType.taa,
    "ascending": AneurysmType.ascending,
}

_PHASE_MAP = {"pre": Phase.pre, "intra": Phase.intra, "post": Phase.post}
_INTERVENTION_MAP = {
    "EVAR": PlannedIntervention.evar,
    "TEVAR": PlannedIntervention.tevar,
    "open_graft": PlannedIntervention.open_graft,
    "surveillance": PlannedIntervention.surveillance,
}
_NOTE_TYPE_MAP = {
    "pre_op_assessment": NoteType.pre_op_assessment,
    "op_note": NoteType.op_note,
    "progress": NoteType.progress,
}


async def seed_users(session: AsyncSession) -> None:
    for u in DEMO_USERS:
        existing = await session.execute(select(User).where(User.email == u["email"]))
        if existing.scalar_one_or_none():
            continue
        session.add(
            User(
                email=u["email"],
                hashed_password=hash_password(u["password"]),
                full_name=u["full_name"],
                role=u["role"],
            )
        )
        log.info("created user: %s (%s)", u["email"], u["role"])
    await session.commit()


async def seed_devices(session: AsyncSession) -> list[Device]:
    devices: list[Device] = []
    for d in DEVICE_CATALOG:
        row = await session.execute(
            select(Device).where(Device.name == d["name"], Device.manufacturer == d["manufacturer"])
        )
        dev = row.scalar_one_or_none()
        if not dev:
            dev = Device(**d)
            session.add(dev)
            await session.flush()
            log.info("created device: %s", d["name"])
        devices.append(dev)
    await session.commit()
    return devices


async def seed_patients(session: AsyncSession, raw: list[dict]) -> list[tuple[Patient, dict]]:
    results: list[tuple[Patient, dict]] = []
    for p in raw:
        row = await session.execute(select(Patient).where(Patient.patient_id == p["patient_id"]))
        if row.scalar_one_or_none():
            continue

        pat = Patient(
            patient_id=p["patient_id"],
            name=p["name"],
            age=p["age"],
            sex=p["sex"],
            mrn=p["mrn"],
            aneurysm_type=_ANEURYSM_TYPE_MAP.get(p.get("aneurysm_type", "")),
            location=p.get("location"),
            max_diameter_mm=p.get("max_diameter_mm"),
            neck_length_mm=p.get("neck_length_mm"),
            neck_angulation_deg=p.get("neck_angulation_deg"),
            neck_diameter_mm=p.get("neck_diameter_mm"),
            iliac_access_min_mm=p.get("iliac_access_min_mm"),
            iliac_access_max_mm=p.get("iliac_access_max_mm"),
            tortuosity=p.get("tortuosity"),
            phase=_PHASE_MAP[p["phase"]],
            planned_intervention=_INTERVENTION_MAP[p["planned_intervention"]],
            surgery_date=p.get("surgery_date"),
        )
        session.add(pat)
        await session.flush()

        c = p["comorbidities"]
        session.add(
            Comorbidity(
                patient_id=pat.id,
                htn=c.get("htn", False),
                dm=c.get("dm", False),
                insulin_dependent=c.get("insulin_dependent", False),
                ckd=c.get("ckd", False),
                copd=c.get("copd", False),
                cad=c.get("cad", False),
                prior_mi=c.get("prior_mi", False),
                afib=c.get("afib", False),
                cvd_stroke=c.get("cvd_stroke", False),
                chf=c.get("chf", False),
                smoking_current=c.get("smoking_current", False),
                smoking_former=c.get("smoking_former", False),
            )
        )

        labs = p["labs"]
        session.add(
            Lab(
                patient_id=pat.id,
                taken_at=datetime.now(UTC),
                creatinine=labs.get("creatinine"),
                egfr=labs.get("egfr"),
                hb=labs.get("hb"),
                platelets=labs.get("platelets"),
                inr=labs.get("inr"),
                hba1c=labs.get("hba1c"),
                bnp=labs.get("bnp"),
                unit=labs.get("unit", "SI"),
            )
        )

        for m in p["medications"]:
            session.add(
                Medication(
                    patient_id=pat.id,
                    name=m["name"],
                    med_class=_MED_CLASS_MAP.get(m["med_class"], MedClass.other),
                    dose=m.get("dose"),
                    route=m.get("route"),
                )
            )

        for v in p["vitals"]:
            session.add(
                Vital(
                    patient_id=pat.id,
                    taken_at=v["taken_at"],
                    rr=v.get("rr"),
                    spo2=v.get("spo2"),
                    on_oxygen=v.get("on_oxygen", False),
                    systolic_bp=v.get("systolic_bp"),
                    heart_rate=v.get("heart_rate"),
                    temp_c=v.get("temp_c"),
                    consciousness=AVPU(v.get("consciousness", "A")),
                )
            )

        n = p["note"]
        note = ClinicalNote(
            patient_id=pat.id,
            note_type=_NOTE_TYPE_MAP[n["note_type"]],
            author_role=n["author_role"],
            timestamp=n["timestamp"],
            body=n["body"],
        )
        session.add(note)
        await session.flush()
        results.append((pat, p))

    await session.commit()
    log.info("seeded %d new patients", len(results))
    return results


def _embed(texts: list[str]) -> list[list[float]]:
    """Encode texts to 384-dim vectors using the bge-small model."""
    from sentence_transformers import SentenceTransformer  # lazy — heavy import

    model = SentenceTransformer("BAAI/bge-small-en-v1.5")
    return model.encode(texts, normalize_embeddings=True, show_progress_bar=False).tolist()


async def embed_knowledge_base(
    patient_rows: list[tuple[Patient, dict]],
    devices: list[Device],
) -> None:
    """Embed guidelines, literature, notes, and device descriptions into Quiver."""
    from quiver import Point

    try:
        guide_texts = [f"{g['title']}\n\n{g['body']}" for g in GUIDELINES_CORPUS]
        guide_vecs = _embed(guide_texts)

        lit_texts = [f"{ref['title']}\n\n{ref['body']}" for ref in LITERATURE_CORPUS]
        lit_vecs = _embed(lit_texts)

        note_sample = patient_rows[:40]
        note_texts = [raw["note"]["body"] for _, raw in note_sample]
        note_vecs = _embed(note_texts)

        dev_texts = [
            (
                f"{d.manufacturer} — {d.name}\n"
                f"Indication: {d.indication}\n"
                f"Neck ≥{d.ifu_min_neck_length_mm} mm, angulation ≤{d.ifu_max_neck_angulation_deg}°\n"
                f"Proximal: {d.ifu_proximal_min_mm}–{d.ifu_proximal_max_mm} mm\n"
                f"Iliac: {d.ifu_iliac_min_mm}–{d.ifu_iliac_max_mm} mm"
            )
            for d in devices
        ]
        dev_vecs = _embed(dev_texts)

        async with get_quiver_client() as q:
            await q.upsert(
                COLLECTION_GUIDELINES,
                [
                    Point(
                        f"guideline-{i:03d}",
                        guide_vecs[i],
                        {
                            "title": GUIDELINES_CORPUS[i]["title"],
                            "section": GUIDELINES_CORPUS[i]["section"],
                        },
                    )
                    for i in range(len(GUIDELINES_CORPUS))
                ],
            )
            await q.upsert(
                COLLECTION_LITERATURE,
                [
                    Point(
                        f"literature-{i:03d}",
                        lit_vecs[i],
                        {
                            "title": LITERATURE_CORPUS[i]["title"],
                            "section": LITERATURE_CORPUS[i]["section"],
                        },
                    )
                    for i in range(len(LITERATURE_CORPUS))
                ],
            )
            await q.upsert(
                COLLECTION_NOTES,
                [
                    Point(
                        f"note-{note_sample[i][0].patient_id}",
                        note_vecs[i],
                        {"patient_id": note_sample[i][0].patient_id},
                    )
                    for i in range(len(note_sample))
                ],
            )
            await q.upsert(
                COLLECTION_DEVICES,
                [
                    Point(
                        f"device-{i:02d}",
                        dev_vecs[i],
                        {"name": devices[i].name, "manufacturer": devices[i].manufacturer},
                    )
                    for i in range(len(devices))
                ],
            )
        log.info("knowledge-base embedding complete")

    except Exception as exc:
        log.warning("quiver embedding skipped (%s) — service may not be running", exc)


async def run(database_url: str | None = None) -> None:
    settings = get_settings()
    url = database_url or settings.database_url

    engine = create_async_engine(url, echo=False, pool_pre_ping=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    try:
        await ensure_collections()
    except Exception as exc:
        log.warning("quiver collection setup skipped (%s)", exc)

    async with async_session() as session:
        log.info("seeding users …")
        await seed_users(session)

        log.info("seeding devices …")
        devices = await seed_devices(session)

        log.info("generating + seeding patients …")
        raw_patients = generate_patients(200)
        patient_rows = await seed_patients(session, raw_patients)

    await engine.dispose()

    log.info("embedding knowledge base …")
    await embed_knowledge_base(patient_rows, devices)

    log.info("seed complete — %d patients, %d devices", len(patient_rows), len(devices))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    asyncio.run(run())
