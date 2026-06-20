from datetime import date, datetime

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


class ComorbiditySchema(BaseModel):
    htn: bool
    dm: bool
    insulin_dependent: bool
    ckd: bool
    copd: bool
    cad: bool
    prior_mi: bool
    afib: bool
    cvd_stroke: bool
    chf: bool
    smoking_current: bool
    smoking_former: bool

    model_config = {"from_attributes": True}


class LabSchema(BaseModel):
    taken_at: datetime
    creatinine: float | None
    egfr: float | None
    hb: float | None
    platelets: float | None
    inr: float | None
    hba1c: float | None
    bnp: float | None
    unit: str

    model_config = {"from_attributes": True}


class MedicationSchema(BaseModel):
    name: str
    med_class: str
    dose: str | None
    route: str | None

    model_config = {"from_attributes": True}


class VitalSchema(BaseModel):
    taken_at: datetime
    rr: int | None
    spo2: float | None
    on_oxygen: bool
    systolic_bp: int | None
    heart_rate: int | None
    temp_c: float | None
    consciousness: str

    model_config = {"from_attributes": True}


class ClinicalNoteSchema(BaseModel):
    note_type: str
    author_role: str
    timestamp: datetime
    body: str

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
    comorbidities: list[ComorbiditySchema] = []
    labs: list[LabSchema] = []
    medications: list[MedicationSchema] = []
    vitals: list[VitalSchema] = []
    clinical_notes: list[ClinicalNoteSchema] = []

    model_config = {"from_attributes": True}
