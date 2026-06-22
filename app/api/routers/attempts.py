from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.core.db import get_db
from app.models.problem import Problem
from app.models.attempt import Attempt
from app.models.step import Step
from app.models.analysis_result import AnalysisResult

from app.schemas.attempt import AttemptCreate, AttemptRead
from app.schemas.step import StepCreate, StepAnalysisRead
from app.services.analysis_service import analyze_step

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


@router.post("/{attempt_id}/steps", response_model=StepAnalysisRead, status_code=201)
def submit_step(attempt_id: UUID, payload: StepCreate, db: Session = Depends(get_db)):
    attempt = db.scalar(select(Attempt).where(Attempt.id == attempt_id))
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")

    if attempt.status != "active":
        raise HTTPException(status_code=400, detail="Attempt is not active")

    last_order = db.scalar(
        select(func.max(Step.step_order)).where(Step.attempt_id == attempt.id)
    )
    next_order = 1 if last_order is None else last_order + 1

    analysis = analyze_step(payload.raw_text)

    step = Step(
        attempt_id=attempt.id,
        step_order=next_order,
        raw_text=payload.raw_text,
        normalized_before=analysis["normalized_before"],
        normalized_after=analysis["normalized_after"],
        operation_type=analysis["operation_type"],
        diagnostics_json={
            "diagnosis_code": analysis["diagnosis_code"],
            "feedback": analysis["feedback"],
            "error_probs": analysis["error_probs"],
            "normalized_before": analysis["normalized_before"],
            "normalized_after": analysis["normalized_after"],
        },
    )
    db.add(step)
    db.flush()

    analysis_result = AnalysisResult(
        step_id=step.id,
        is_valid=analysis["is_valid"],
        soft_score=analysis["soft_score"],
        math_score=analysis["math_score"],
        logic_score=analysis["logic_score"],
        condition_score=analysis["condition_score"],
        goal_score=analysis["goal_score"],
        error_probs_json=analysis["error_probs"],
        feedback_json=analysis["feedback"],
    )
    db.add(analysis_result)

    db.commit()
    db.refresh(step)

    return {
        "step_id": step.id,
        "step_order": step.step_order,
        "raw_text": step.raw_text,
        "normalized_before": step.normalized_before,
        "normalized_after": step.normalized_after,
        "is_valid": analysis_result.is_valid,
        "soft_score": analysis_result.soft_score,
        "operation_type": step.operation_type,
        "diagnosis_code": analysis["diagnosis_code"],
        "feedback": analysis_result.feedback_json,
        "error_probs": analysis_result.error_probs_json or {},
    }
