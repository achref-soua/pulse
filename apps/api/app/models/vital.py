import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import UUIDMixin

if TYPE_CHECKING:
    from app.models.patient import Patient


class AVPU(str, enum.Enum):
    A = "A"  # Alert
    V = "V"  # Voice
    P = "P"  # Pain
    U = "U"  # Unresponsive


class Vital(Base, UUIDMixin):
    __tablename__ = "vitals"

    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False
    )
    taken_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    rr: Mapped[int | None] = mapped_column(Integer, nullable=True)
    spo2: Mapped[float | None] = mapped_column(Float, nullable=True)
    on_oxygen: Mapped[bool] = mapped_column(Boolean, default=False)
    systolic_bp: Mapped[int | None] = mapped_column(Integer, nullable=True)
    heart_rate: Mapped[int | None] = mapped_column(Integer, nullable=True)
    temp_c: Mapped[float | None] = mapped_column(Float, nullable=True)
    consciousness: Mapped[AVPU] = mapped_column(Enum(AVPU), default=AVPU.A)

    patient: Mapped["Patient"] = relationship("Patient", back_populates="vitals")
