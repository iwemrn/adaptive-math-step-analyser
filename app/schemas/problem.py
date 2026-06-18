from pydantic import BaseModel, ConfigDict
from uuid import UUID


class ProblemCreate(BaseModel):
    topic: str
    title: str
    statement: str
    expected_answer: str | None = None
    metadata_json: dict | None = None


class ProblemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    topic: str
    title: str
    statement: str
    expected_answer: str | None = None
    metadata_json: dict | None = None
