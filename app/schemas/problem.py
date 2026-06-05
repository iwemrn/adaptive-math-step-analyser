from pydantic import BaseModel
from uuid import UUID


class ProblemCreate(BaseModel):
    topic: str
    title: str
    statement: str
    expected_answer: str | None = None
    metadata_json: dict | None = None


class ProblemRead(BaseModel):
    id: UUID
    topic: str
    title: str
    statement: str
    expected_answer: str | None = None
    metadata_json: dict | None = None

    class Config:
        from_attributes = True
