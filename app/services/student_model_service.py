from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.student_profile import StudentProfile


DEFAULT_PROFILE_KEY = "demo"
NON_MISCONCEPTION_CODES = {
    "equivalent_transition",
    "single_expression",
}


def get_or_create_profile(db: Session, profile_key: str = DEFAULT_PROFILE_KEY) -> StudentProfile:
    profile = db.scalar(
        select(StudentProfile).where(StudentProfile.profile_key == profile_key)
    )
    if profile:
        return profile

    profile = StudentProfile(
        profile_key=profile_key,
        overall_mastery=0.0,
        total_steps=0,
        correct_steps=0,
        incorrect_steps=0,
        topic_mastery_json={},
        misconception_stats_json={},
    )
    db.add(profile)
    db.flush()
    return profile


def _update_topic_mastery(profile: StudentProfile, topic: str, is_valid: bool) -> None:
    topic_stats = dict(profile.topic_mastery_json or {})
    current_topic = dict(
        topic_stats.get(
            topic,
            {
                "total_steps": 0,
                "correct_steps": 0,
                "incorrect_steps": 0,
                "mastery": 0.0,
            },
        )
    )

    current_topic["total_steps"] += 1
    if is_valid:
        current_topic["correct_steps"] += 1
    else:
        current_topic["incorrect_steps"] += 1

    total = current_topic["total_steps"]
    correct = current_topic["correct_steps"]
    current_topic["mastery"] = round(correct / total, 2) if total > 0 else 0.0

    topic_stats[topic] = current_topic
    profile.topic_mastery_json = topic_stats


def _update_misconceptions(profile: StudentProfile, diagnosis_code: str | None) -> None:
    if not diagnosis_code:
        return

    if diagnosis_code in NON_MISCONCEPTION_CODES:
        return

    misconception_stats = dict(profile.misconception_stats_json or {})
    misconception_stats[diagnosis_code] = misconception_stats.get(diagnosis_code, 0) + 1
    profile.misconception_stats_json = misconception_stats


def update_profile_after_step(
    db: Session,
    topic: str,
    is_valid: bool,
    diagnosis_code: str | None,
    profile_key: str = DEFAULT_PROFILE_KEY,
) -> StudentProfile:
    profile = get_or_create_profile(db, profile_key=profile_key)

    profile.total_steps += 1
    if is_valid:
        profile.correct_steps += 1
    else:
        profile.incorrect_steps += 1

    if profile.total_steps > 0:
        profile.overall_mastery = round(profile.correct_steps / profile.total_steps, 2)
    else:
        profile.overall_mastery = 0.0

    _update_topic_mastery(profile, topic=topic, is_valid=is_valid)
    _update_misconceptions(profile, diagnosis_code=diagnosis_code)

    db.add(profile)
    db.flush()
    return profile
