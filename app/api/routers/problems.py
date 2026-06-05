from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.db import get_db
from app.models.problem import Problem
from app.schemas.problem import ProblemCreate, ProblemRead

router = APIRouter()


@router.post("", response_model=ProblemRead, status_code=201)
def create_problem(payload: ProblemCreate, db: Session = Depends(get_db)):
    problem = Problem(
        topic=payload.topic,
        title=payload.title,
        statement=payload.statement,
        expected_answer=payload.expected_answer,
        metadata_json=payload.metadata_json,
    )
    db.add(problem)
    db.commit()
    db.refresh(problem)
    return problem


@router.get("/{problem_id}", response_model=ProblemRead)
def get_problem(problem_id: UUID, db: Session = Depends(get_db)):
    problem = db.scalar(select(Problem).where(Problem.id == problem_id))
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    return problem
