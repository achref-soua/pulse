from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    patient_id: str | None = None
    thread_id: str | None = None


class NLCohortRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)


class CohortFilters(BaseModel):
    """Structured roster filters extracted from a natural-language query."""

    phase: str | None = None
    planned_intervention: str | None = None
    aneurysm_type: str | None = None
    sex: str | None = None
    min_diameter_mm: float | None = None
    min_age: int | None = None
    max_age: int | None = None


class NLCohortResponse(BaseModel):
    query: str
    filters: CohortFilters
    total: int
    patient_ids: list[str]


class KBItem(BaseModel):
    id: str
    type: str
    title: str
    section: str
    source: str


class SourceDoc(BaseModel):
    id: str
    type: str
    title: str
    body: str
    source: str
    score: float | None = None


class PatientSummaryResponse(BaseModel):
    patient_id: str
    summary: str
    sources: list[SourceDoc]
