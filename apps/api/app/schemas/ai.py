from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    patient_id: str | None = None
    thread_id: str | None = None


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
