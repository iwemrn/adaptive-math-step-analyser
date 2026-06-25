from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.schemas.profile import ProfileResetRead
from app.services.problem_seed_service import seed_default_problems
from app.services.profile_admin_service import reset_profile

router = APIRouter()


@router.post("/profiles/{profile_key}/reset", response_model=ProfileResetRead)
def reset_profile_route(profile_key: str, db: Session = Depends(get_db)):
    reset_profile(db, profile_key=profile_key)
    return {
        "profile_key": profile_key,
        "status": "reset",
    }


@router.post("/seed-default-problems")
def seed_default_problems_route(db: Session = Depends(get_db)):
    return seed_default_problems(db)
