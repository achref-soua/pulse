import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import UUIDMixin

if TYPE_CHECKING:
    from app.models.patient import Patient


class MedClass(enum.StrEnum):
    antiplatelet = "antiplatelet"
    anticoagulant = "anticoagulant"
    statin = "statin"
    beta_blocker = "beta_blocker"
    acei_arb = "ACEi/ARB"
    diuretic = "diuretic"
    other = "other"


class Medication(Base, UUIDMixin):
    __tablename__ = "medications"

    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    med_class: Mapped[MedClass] = mapped_column(
        Enum(MedClass, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=MedClass.other,
    )
    dose: Mapped[str | None] = mapped_column(String(50), nullable=True)
    route: Mapped[str | None] = mapped_column(String(20), nullable=True)

    patient: Mapped["Patient"] = relationship("Patient", back_populates="medications")
