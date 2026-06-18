from pydantic import BaseModel, ConfigDict
from uuid import UUID


class AttemptCreate(BaseModel):
    problem_id: UUID


class AttemptRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    problem_id: UUID
    status: str
