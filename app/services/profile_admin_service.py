from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.student_profile import StudentProfile


def reset_profile(db: Session, profile_key: str) -> bool:
    profile = db.scalar(
        select(StudentProfile).where(StudentProfile.profile_key == profile_key)
    )
    if not profile:
        return False

    profile.overall_mastery = 0.0
    profile.total_steps = 0
    profile.correct_steps = 0
    profile.incorrect_steps = 0
    profile.topic_mastery_json = {}
    profile.misconception_stats_json = {}

    db.add(profile)
    db.commit()
    return True


def delete_profile(db: Session, profile_key: str) -> bool:
    result = db.execute(
        delete(StudentProfile).where(StudentProfile.profile_key == profile_key)
    )
    db.commit()
    return result.rowcount > 0
