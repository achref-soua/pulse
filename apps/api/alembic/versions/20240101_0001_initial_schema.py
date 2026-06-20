"""initial schema

Revision ID: 0001
Revises:
Create Date: 2024-01-01 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # users
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("hashed_password", sa.String(128), nullable=False),
        sa.Column("full_name", sa.String(200), nullable=False),
        sa.Column("role", sa.Enum("surgeon", "anesthetist", "nurse", "admin", name="userrole"), nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # patients
    op.create_table(
        "patients",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("patient_id", sa.String(10), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("age", sa.Integer, nullable=False),
        sa.Column("dob", sa.Date, nullable=True),
        sa.Column("sex", sa.String(1), nullable=False),
        sa.Column("mrn", sa.String(20), nullable=False),
        sa.Column("aneurysm_type", sa.Enum("infrarenal_AAA", "juxtarenal_AAA", "TAA", "ascending", name="aneurysmtype"), nullable=True),
        sa.Column("location", sa.String(100), nullable=True),
        sa.Column("max_diameter_mm", sa.Float, nullable=True),
        sa.Column("neck_length_mm", sa.Float, nullable=True),
        sa.Column("neck_angulation_deg", sa.Float, nullable=True),
        sa.Column("neck_diameter_mm", sa.Float, nullable=True),
        sa.Column("iliac_access_min_mm", sa.Float, nullable=True),
        sa.Column("iliac_access_max_mm", sa.Float, nullable=True),
        sa.Column("tortuosity", sa.String(20), nullable=True),
        sa.Column("ct_scan_date", sa.Date, nullable=True),
        sa.Column("phase", sa.Enum("pre", "intra", "post", name="phase"), nullable=False),
        sa.Column("planned_intervention", sa.Enum("EVAR", "TEVAR", "open_graft", "surveillance", name="plannedintervention"), nullable=False),
        sa.Column("surgery_date", sa.Date, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_patients_patient_id", "patients", ["patient_id"], unique=True)
    op.create_index("ix_patients_mrn", "patients", ["mrn"], unique=True)

    # comorbidities
    op.create_table(
        "comorbidities",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("patient_id", UUID(as_uuid=True), sa.ForeignKey("patients.id", ondelete="CASCADE"), nullable=False),
        sa.Column("htn", sa.Boolean, server_default="false"),
        sa.Column("dm", sa.Boolean, server_default="false"),
        sa.Column("insulin_dependent", sa.Boolean, server_default="false"),
        sa.Column("ckd", sa.Boolean, server_default="false"),
        sa.Column("copd", sa.Boolean, server_default="false"),
        sa.Column("cad", sa.Boolean, server_default="false"),
        sa.Column("prior_mi", sa.Boolean, server_default="false"),
        sa.Column("afib", sa.Boolean, server_default="false"),
        sa.Column("cvd_stroke", sa.Boolean, server_default="false"),
        sa.Column("chf", sa.Boolean, server_default="false"),
        sa.Column("smoking_current", sa.Boolean, server_default="false"),
        sa.Column("smoking_former", sa.Boolean, server_default="false"),
    )

    # labs
    op.create_table(
        "labs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("patient_id", UUID(as_uuid=True), sa.ForeignKey("patients.id", ondelete="CASCADE"), nullable=False),
        sa.Column("taken_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("creatinine", sa.Float, nullable=True),
        sa.Column("egfr", sa.Float, nullable=True),
        sa.Column("hb", sa.Float, nullable=True),
        sa.Column("platelets", sa.Float, nullable=True),
        sa.Column("inr", sa.Float, nullable=True),
        sa.Column("hba1c", sa.Float, nullable=True),
        sa.Column("bnp", sa.Float, nullable=True),
        sa.Column("unit", sa.String(20), server_default="SI"),
    )

    # medications
    op.create_table(
        "medications",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("patient_id", UUID(as_uuid=True), sa.ForeignKey("patients.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("med_class", sa.Enum("antiplatelet", "anticoagulant", "statin", "beta_blocker", "ACEi/ARB", "diuretic", "other", name="medclass"), nullable=False),
        sa.Column("dose", sa.String(50), nullable=True),
        sa.Column("route", sa.String(20), nullable=True),
    )

    # vitals
    op.create_table(
        "vitals",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("patient_id", UUID(as_uuid=True), sa.ForeignKey("patients.id", ondelete="CASCADE"), nullable=False),
        sa.Column("taken_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("rr", sa.Integer, nullable=True),
        sa.Column("spo2", sa.Float, nullable=True),
        sa.Column("on_oxygen", sa.Boolean, server_default="false"),
        sa.Column("systolic_bp", sa.Integer, nullable=True),
        sa.Column("heart_rate", sa.Integer, nullable=True),
        sa.Column("temp_c", sa.Float, nullable=True),
        sa.Column("consciousness", sa.Enum("A", "V", "P", "U", name="avpu"), server_default="A"),
    )

    # devices
    op.create_table(
        "devices",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("manufacturer", sa.String(200), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("indication", sa.String(50), nullable=False),
        sa.Column("ifu_proximal_min_mm", sa.Float, nullable=False),
        sa.Column("ifu_proximal_max_mm", sa.Float, nullable=False),
        sa.Column("ifu_distal_min_mm", sa.Float, nullable=False),
        sa.Column("ifu_distal_max_mm", sa.Float, nullable=False),
        sa.Column("ifu_length_options_mm", sa.JSON, nullable=False),
        sa.Column("ifu_min_neck_length_mm", sa.Float, nullable=False),
        sa.Column("ifu_max_neck_angulation_deg", sa.Float, nullable=False),
        sa.Column("ifu_iliac_min_mm", sa.Float, nullable=False),
        sa.Column("ifu_iliac_max_mm", sa.Float, nullable=False),
        sa.Column("sheath_fr", sa.Integer, nullable=False),
        sa.Column("contraindications", sa.JSON, nullable=False),
        sa.Column("deployment_steps", sa.JSON, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_devices_name", "devices", ["name"])

    # clinical_notes
    op.create_table(
        "clinical_notes",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("patient_id", UUID(as_uuid=True), sa.ForeignKey("patients.id", ondelete="CASCADE"), nullable=False),
        sa.Column("note_type", sa.Enum("referral", "pre_op_assessment", "op_note", "progress", "discharge", name="notetype"), nullable=False),
        sa.Column("author_role", sa.String(20), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("body", sa.Text, nullable=False),
        sa.Column("quiver_doc_id", sa.String(100), nullable=True),
    )

    # conversations
    op.create_table(
        "conversations",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(200), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    # messages
    op.create_table(
        "messages",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("conversation_id", UUID(as_uuid=True), sa.ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("routing_metadata", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    # risk_assessments
    op.create_table(
        "risk_assessments",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("patient_id", UUID(as_uuid=True), sa.ForeignKey("patients.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("score_type", sa.String(50), nullable=False),
        sa.Column("inputs", sa.JSON, nullable=False),
        sa.Column("result", sa.JSON, nullable=False),
        sa.Column("computed_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    # audit_log
    op.create_table(
        "audit_log",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("entity", sa.String(100), nullable=False),
        sa.Column("entity_id", sa.String(100), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("audit_log")
    op.drop_table("risk_assessments")
    op.drop_table("messages")
    op.drop_table("conversations")
    op.drop_table("clinical_notes")
    op.drop_table("devices")
    op.drop_table("vitals")
    op.drop_table("medications")
    op.drop_table("labs")
    op.drop_table("comorbidities")
    op.drop_table("patients")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS userrole")
    op.execute("DROP TYPE IF EXISTS aneurysmtype")
    op.execute("DROP TYPE IF EXISTS phase")
    op.execute("DROP TYPE IF EXISTS plannedintervention")
    op.execute("DROP TYPE IF EXISTS medclass")
    op.execute("DROP TYPE IF EXISTS notetype")
    op.execute("DROP TYPE IF EXISTS avpu")
