from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.schemas.practice import NextProblemRecommendationRead
from app.services.next_problem_service import choose_next_problem

router = APIRouter()


@router.get("/next-problem/{profile_key}", response_model=NextProblemRecommendationRead)
def get_next_problem(profile_key: str, db: Session = Depends(get_db)):
    result = choose_next_problem(db, profile_key=profile_key)
    if not result:
        raise HTTPException(status_code=404, detail="No problems available for recommendation")
    return result
