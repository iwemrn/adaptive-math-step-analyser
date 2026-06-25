from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.schemas.profile import ProfileWithRecommendationsRead
from app.services.recommendation_service import build_recommendations
from app.services.student_model_service import get_or_create_profile

router = APIRouter()


@router.get("/{profile_key}", response_model=ProfileWithRecommendationsRead)
def get_profile(profile_key: str, db: Session = Depends(get_db)):
    profile = get_or_create_profile(db, profile_key=profile_key)
    recommendations = build_recommendations(profile)

    return {
        "id": profile.id,
        "profile_key": profile.profile_key,
        "overall_mastery": profile.overall_mastery,
        "total_steps": profile.total_steps,
        "correct_steps": profile.correct_steps,
        "incorrect_steps": profile.incorrect_steps,
        "topic_mastery_json": profile.topic_mastery_json or {},
        "misconception_stats_json": profile.misconception_stats_json or {},
        "recommendations": recommendations,
    }
