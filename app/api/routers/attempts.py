from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.db import get_db
from app.models.problem import Problem
from app.models.attempt import Attempt
from app.schemas.attempt import AttemptCreate, AttemptRead

router = APIRouter()


@router.post("", response_model=AttemptRead, status_code=201)
def create_attempt(payload: AttemptCreate, db: Session = Depends(get_db)):
    problem = db.scalar(select(Problem).where(Problem.id == payload.problem_id))
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    attempt = Attempt(
        problem_id=payload.problem_id,
        status="active",
        user_id=None,
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return attempt


@router.get("/{attempt_id}", response_model=AttemptRead)
def get_attempt(attempt_id: UUID, db: Session = Depends(get_db)):
    attempt = db.scalar(select(Attempt).where(Attempt.id == attempt_id))
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    return attempt
