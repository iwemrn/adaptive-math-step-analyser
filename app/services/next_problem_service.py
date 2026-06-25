from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.problem import Problem
from app.models.student_profile import StudentProfile
from app.services.student_model_service import get_or_create_profile


DIAGNOSIS_TOPIC_MAP = {
    "sign_error": "linear_equations",
    "arithmetic_error": "linear_equations",
    "invalid_transform": "linear_equations",
    "possible_domain_loss": "fractions",
    "division_by_zero": "fractions",
    "parse_error": "linear_equations",
    "math_parse_error": "linear_equations",
}

DIFFICULTY_ORDER = {
    "easy": 1,
    "medium": 2,
    "hard": 3,
}


def _pick_primary_diagnosis(profile: StudentProfile) -> str | None:
    misconception_stats = dict(profile.misconception_stats_json or {})
    if not misconception_stats:
        return None

    sorted_items = sorted(
        misconception_stats.items(),
        key=lambda item: item[1],
        reverse=True,
    )
    return sorted_items[0][0]


def _pick_target_topic(profile: StudentProfile, diagnosis_code: str | None) -> str | None:
    if diagnosis_code and diagnosis_code in DIAGNOSIS_TOPIC_MAP:
        return DIAGNOSIS_TOPIC_MAP[diagnosis_code]

    topic_stats = dict(profile.topic_mastery_json or {})
    if not topic_stats:
        return None

    weak_topics = []
    for topic, stats in topic_stats.items():
        mastery = stats.get("mastery", 0.0)
        total_steps = stats.get("total_steps", 0)
        if total_steps > 0:
            weak_topics.append((topic, mastery))

    if not weak_topics:
        return None

    weak_topics.sort(key=lambda item: item[1])
    return weak_topics[0][0]


def _pick_target_difficulty(profile: StudentProfile, target_topic: str | None) -> str:
    topic_stats = dict(profile.topic_mastery_json or {})

    mastery = None
    if target_topic and target_topic in topic_stats:
        mastery = topic_stats[target_topic].get("mastery", 0.0)

    if mastery is None:
        mastery = profile.overall_mastery

    if mastery < 0.4:
        return "easy"
    if mastery < 0.75:
        return "medium"
    return "hard"


def _score_problem(
    problem: Problem,
    target_topic: str | None,
    target_diagnosis: str | None,
    target_difficulty: str,
) -> tuple[int, list[str]]:
    metadata = dict(problem.metadata_json or {})
    reason_parts: list[str] = []
    score = 0

    if target_topic and problem.topic == target_topic:
        score += 50
        reason_parts.append(f"совпадает тема '{target_topic}'")

    focus_diagnosis = metadata.get("focus_diagnosis")
    if target_diagnosis and focus_diagnosis == target_diagnosis:
        score += 30
        reason_parts.append(f"нацелена на ошибку '{target_diagnosis}'")

    difficulty = metadata.get("difficulty")
    if difficulty == target_difficulty:
        score += 15
        reason_parts.append(f"подходит уровень сложности '{target_difficulty}'")
    elif difficulty:
        current_order = DIFFICULTY_ORDER.get(difficulty, 2)
        target_order = DIFFICULTY_ORDER.get(target_difficulty, 2)

        if abs(current_order - target_order) == 1:
            score += 5
            reason_parts.append("уровень сложности близок к целевому")

    if not metadata:
        score += 1
        reason_parts.append("задача без дополнительной разметки")

    return score, reason_parts


def choose_next_problem(db: Session, profile_key: str) -> dict | None:
    profile = get_or_create_profile(db, profile_key=profile_key)

    problems = list(db.scalars(select(Problem)).all())
    if not problems:
        return None

    target_diagnosis = _pick_primary_diagnosis(profile)
    target_topic = _pick_target_topic(profile, target_diagnosis)
    target_difficulty = _pick_target_difficulty(profile, target_topic)

    best_problem = None
    best_score = -10**9
    best_reasons: list[str] = []

    for problem in problems:
        score, reasons = _score_problem(
            problem=problem,
            target_topic=target_topic,
            target_diagnosis=target_diagnosis,
            target_difficulty=target_difficulty,
        )

        if score > best_score:
            best_score = score
            best_problem = problem
            best_reasons = reasons

    if best_problem is None:
        return None

    reason = "Рекомендация выбрана автоматически"
    if best_reasons:
        reason = "Рекомендация выбрана, потому что " + ", ".join(best_reasons) + "."

    return {
        "problem_id": best_problem.id,
        "topic": best_problem.topic,
        "title": best_problem.title,
        "statement": best_problem.statement,
        "expected_answer": best_problem.expected_answer,
        "metadata_json": best_problem.metadata_json or {},
        "based_on_diagnosis": target_diagnosis,
        "target_topic": target_topic,
        "target_difficulty": target_difficulty,
        "reason": reason,
    }
