import enum
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, Enum, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.clinical_note import ClinicalNote
    from app.models.comorbidity import Comorbidity
    from app.models.lab import Lab
    from app.models.medication import Medication
    from app.models.vital import Vital


class AneurysmType(enum.StrEnum):
    infrarenal_aaa = "infrarenal_AAA"
    juxtarenal_aaa = "juxtarenal_AAA"
    taa = "TAA"
    ascending = "ascending"


class Phase(enum.StrEnum):
    pre = "pre"
    intra = "intra"
    post = "post"


class PlannedIntervention(enum.StrEnum):
    evar = "EVAR"
    tevar = "TEVAR"
    open_graft = "open_graft"
    surveillance = "surveillance"


class Patient(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "patients"

    # Identity
    patient_id: Mapped[str] = mapped_column(String(10), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    dob: Mapped[date | None] = mapped_column(Date, nullable=True)
    sex: Mapped[str] = mapped_column(String(1), nullable=False)  # M / F
    mrn: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)

    # Aortic anatomy
    aneurysm_type: Mapped[AneurysmType | None] = mapped_column(Enum(AneurysmType), nullable=True)
    location: Mapped[str | None] = mapped_column(String(100), nullable=True)
    max_diameter_mm: Mapped[float | None] = mapped_column(Float, nullable=True)
    neck_length_mm: Mapped[float | None] = mapped_column(Float, nullable=True)
    neck_angulation_deg: Mapped[float | None] = mapped_column(Float, nullable=True)
    neck_diameter_mm: Mapped[float | None] = mapped_column(Float, nullable=True)
    iliac_access_min_mm: Mapped[float | None] = mapped_column(Float, nullable=True)
    iliac_access_max_mm: Mapped[float | None] = mapped_column(Float, nullable=True)
    tortuosity: Mapped[str | None] = mapped_column(String(20), nullable=True)
    ct_scan_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Status
    phase: Mapped[Phase] = mapped_column(Enum(Phase), nullable=False, default=Phase.pre)
    planned_intervention: Mapped[PlannedIntervention] = mapped_column(
        Enum(PlannedIntervention), nullable=False, default=PlannedIntervention.surveillance
    )
    surgery_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Relationships
    comorbidities: Mapped[list["Comorbidity"]] = relationship(
        "Comorbidity", back_populates="patient", cascade="all, delete-orphan"
    )
    labs: Mapped[list["Lab"]] = relationship("Lab", back_populates="patient", cascade="all, delete-orphan")
    medications: Mapped[list["Medication"]] = relationship(
        "Medication", back_populates="patient", cascade="all, delete-orphan"
    )
    vitals: Mapped[list["Vital"]] = relationship(
        "Vital",
        back_populates="patient",
        cascade="all, delete-orphan",
        order_by="Vital.taken_at",
    )
    clinical_notes: Mapped[list["ClinicalNote"]] = relationship(
        "ClinicalNote",
        back_populates="patient",
        cascade="all, delete-orphan",
        order_by="ClinicalNote.timestamp",
    )
