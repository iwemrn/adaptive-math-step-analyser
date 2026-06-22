from pydantic import BaseModel
from uuid import UUID


class StepCreate(BaseModel):
    raw_text: str


class FeedbackRead(BaseModel):
    type: str
    text: str


class StepAnalysisRead(BaseModel):
    step_id: UUID
    step_order: int
    raw_text: str
    normalized_before: str | None = None
    normalized_after: str | None = None
    is_valid: bool
    soft_score: float
    operation_type: str | None = None
    diagnosis_code: str | None = None
    feedback: FeedbackRead
    error_probs: dict = {}
