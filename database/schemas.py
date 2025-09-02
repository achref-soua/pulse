# schemas.py
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import date, datetime


# --------------------------
# Patient Schema
# --------------------------
class Patient(BaseModel):
    patient_id: str = Field(..., description="Unique patient identifier (e.g., P050)")
    name: str
    age: int
    sex: str
    risk_factors: Optional[str] = None
    diagnosis: Optional[str] = None
    aneurysm_diameter_cm: Optional[float] = None
    aneurysm_location: Optional[str] = None
    ct_scan_date: Optional[date] = None
    planned_intervention: Optional[str] = None
    text: str

    @field_validator("sex")
    def validate_sex(cls, v):
        allowed = {"Male", "Female", "Other"}
        if v not in allowed:
            raise ValueError(f"Sex must be one of {allowed}")
        return v


# --------------------------
# Device Schema
# --------------------------
class DeviceSizing(BaseModel):
    proximal_diameter_range_mm: List[int]
    distal_diameter_range_mm: List[int]
    length_options_mm: List[int]


class DeviceAnatomyReq(BaseModel):
    min_neck_length_mm: int
    max_neck_angulation_deg: int
    iliac_access_min_mm: int
    iliac_access_max_mm: int


class DeviceDeliverySystem(BaseModel):
    sheath_size_fr: int
    flexibility: str


class Device(BaseModel):
    device_id: str
    manufacturer: str
    device_name: str
    indication: str
    sizing: DeviceSizing
    anatomical_requirements: DeviceAnatomyReq
    contraindications: List[str]
    delivery_system: DeviceDeliverySystem
    deployment_steps: List[str]
    text: str


# --------------------------
# Clinical Notes Schema
# --------------------------
class Note(BaseModel):
    note_id: str
    patient_id: str
    note_type: str
    timestamp: datetime
    text: str


# --------------------------
# Literature Schema
# --------------------------
class Literature(BaseModel):
    doc_id: str
    section: str
    text: str
    source: str


# --------------------------
# Guideline Schema
# --------------------------
class Guideline(BaseModel):
    doc_id: str
    section: str
    text: str
    source: str


# --------------------------
# Wrapper for All Collections
# --------------------------
class KnowledgeBase(BaseModel):
    patients: List[Patient]
    devices: List[Device]
    notes: List[Note]
    literature: List[Literature]
    guidelines: List[Guideline]

    def patient_exists(self, patient_id: str) -> bool:
        """Check if patient exists in KB"""
        return any(p.patient_id == patient_id for p in self.patients)

    def get_patient(self, patient_id: str) -> Optional[Patient]:
        """Return patient object if exists, else None"""
        return next((p for p in self.patients if p.patient_id == patient_id), None)
