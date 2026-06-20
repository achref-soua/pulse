from sqlalchemy import JSON, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class Device(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "devices"

    manufacturer: Mapped[str] = mapped_column(String(200), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    indication: Mapped[str] = mapped_column(String(50), nullable=False)  # EVAR | TEVAR

    # IFU envelope
    ifu_proximal_min_mm: Mapped[float] = mapped_column(Float, nullable=False)
    ifu_proximal_max_mm: Mapped[float] = mapped_column(Float, nullable=False)
    ifu_distal_min_mm: Mapped[float] = mapped_column(Float, nullable=False)
    ifu_distal_max_mm: Mapped[float] = mapped_column(Float, nullable=False)
    ifu_length_options_mm: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    ifu_min_neck_length_mm: Mapped[float] = mapped_column(Float, nullable=False)
    ifu_max_neck_angulation_deg: Mapped[float] = mapped_column(Float, nullable=False)
    ifu_iliac_min_mm: Mapped[float] = mapped_column(Float, nullable=False)
    ifu_iliac_max_mm: Mapped[float] = mapped_column(Float, nullable=False)
    sheath_fr: Mapped[int] = mapped_column(Integer, nullable=False)

    contraindications: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    deployment_steps: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
