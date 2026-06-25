from uuid import UUID

from pydantic import BaseModel, Field


class PracticeGenerateRequest(BaseModel):
    profile_key: str | None = None
    topic: str | None = None
    difficulty: str | None = None
    focus_diagnosis: str | None = None


class NextProblemRecommendationRead(BaseModel):
    problem_id: UUID
    topic: str
    title: str
    statement: str
    expected_answer: str | None = None
    metadata_json: dict = Field(default_factory=dict)

    based_on_diagnosis: str | None = None
    target_topic: str | None = None
    target_difficulty: str | None = None
    reason: str
