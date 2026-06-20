import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import UUIDMixin

if TYPE_CHECKING:
    from app.models.patient import Patient


class Comorbidity(Base, UUIDMixin):
    __tablename__ = "comorbidities"

    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False
    )

    htn: Mapped[bool] = mapped_column(Boolean, default=False)
    dm: Mapped[bool] = mapped_column(Boolean, default=False)
    insulin_dependent: Mapped[bool] = mapped_column(Boolean, default=False)
    ckd: Mapped[bool] = mapped_column(Boolean, default=False)
    copd: Mapped[bool] = mapped_column(Boolean, default=False)
    cad: Mapped[bool] = mapped_column(Boolean, default=False)
    prior_mi: Mapped[bool] = mapped_column(Boolean, default=False)
    afib: Mapped[bool] = mapped_column(Boolean, default=False)
    cvd_stroke: Mapped[bool] = mapped_column(Boolean, default=False)
    chf: Mapped[bool] = mapped_column(Boolean, default=False)
    smoking_current: Mapped[bool] = mapped_column(Boolean, default=False)
    smoking_former: Mapped[bool] = mapped_column(Boolean, default=False)

    patient: Mapped["Patient"] = relationship("Patient", back_populates="comorbidities")
