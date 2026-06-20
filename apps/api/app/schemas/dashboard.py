from pydantic import BaseModel


class PhaseBreakdown(BaseModel):
    pre: int
    intra: int
    post: int


class DashboardStats(BaseModel):
    total_patients: int
    by_phase: PhaseBreakdown
    high_news2_count: int
    borderline_anatomy_count: int
    challenging_anatomy_count: int
    upcoming_procedures: int
