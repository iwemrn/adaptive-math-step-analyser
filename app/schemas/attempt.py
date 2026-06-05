from pydantic import BaseModel
from uuid import UUID


class AttemptCreate(BaseModel):
    problem_id: UUID


class AttemptRead(BaseModel):
    id: UUID
    problem_id: UUID
    status: str

    class Config:
        from_attributes = True
