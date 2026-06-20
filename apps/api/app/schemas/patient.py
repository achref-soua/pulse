from datetime import date
from typing import Any

from pydantic import BaseModel


class PatientListItem(BaseModel):
    patient_id: str
    name: str
    age: int
    sex: str
    aneurysm_type: str | None
    max_diameter_mm: float | None
    phase: str
    planned_intervention: str

    model_config = {"from_attributes": True}


class PatientResponse(BaseModel):
    patient_id: str
    name: str
    age: int
    dob: date | None
    sex: str
    mrn: str
    aneurysm_type: str | None
    location: str | None
    max_diameter_mm: float | None
    neck_length_mm: float | None
    neck_angulation_deg: float | None
    neck_diameter_mm: float | None
    iliac_access_min_mm: float | None
    iliac_access_max_mm: float | None
    tortuosity: str | None
    ct_scan_date: date | None
    phase: str
    planned_intervention: str
    surgery_date: date | None
    comorbidities: list[Any] = []
    labs: list[Any] = []
    medications: list[Any] = []
    vitals: list[Any] = []
    clinical_notes: list[Any] = []

    model_config = {"from_attributes": True}
