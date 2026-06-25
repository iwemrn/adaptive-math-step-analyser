from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RecommendationRead(BaseModel):
    code: str
    title: str
    description: str


class ProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    profile_key: str
    overall_mastery: float
    total_steps: int
    correct_steps: int
    incorrect_steps: int
    topic_mastery_json: dict = Field(default_factory=dict)
    misconception_stats_json: dict = Field(default_factory=dict)


class ProfileWithRecommendationsRead(ProfileRead):
    recommendations: list[RecommendationRead] = Field(default_factory=list)


class ProfileResetRead(BaseModel):
    profile_key: str
    status: str
