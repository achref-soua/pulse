import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import UUIDMixin

if TYPE_CHECKING:
    from app.models.patient import Patient


class NoteType(str, enum.Enum):
    referral = "referral"
    pre_op_assessment = "pre_op_assessment"
    op_note = "op_note"
    progress = "progress"
    discharge = "discharge"


class ClinicalNote(Base, UUIDMixin):
    __tablename__ = "clinical_notes"

    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False
    )
    note_type: Mapped[NoteType] = mapped_column(Enum(NoteType), nullable=False)
    author_role: Mapped[str] = mapped_column(String(20), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    quiver_doc_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    patient: Mapped["Patient"] = relationship("Patient", back_populates="clinical_notes")
