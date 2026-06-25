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


def _pick_weak_topic_from_profile(profile: StudentProfile) -> str | None:
    topic_stats = dict(profile.topic_mastery_json or {})
    if not topic_stats:
        return None

    weak_topics = []
    for topic, stats in topic_stats.items():
        mastery = stats.get("mastery", 0.0)
        total_steps = stats.get("total_steps", 0)
        if total_steps > 0:
            weak_topics.append((topic, mastery, total_steps))

    if not weak_topics:
        return None

    weak_topics.sort(key=lambda item: (item[1], -item[2]))
    return weak_topics[0][0]


def _pick_target_topic(profile: StudentProfile, diagnosis_code: str | None) -> str | None:
    weak_topic = _pick_weak_topic_from_profile(profile)
    if weak_topic:
        return weak_topic

    if diagnosis_code and diagnosis_code in DIAGNOSIS_TOPIC_MAP:
        return DIAGNOSIS_TOPIC_MAP[diagnosis_code]

    return None


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


def _pick_target_max_steps(profile: StudentProfile, target_topic: str | None) -> int:
    topic_stats = dict(profile.topic_mastery_json or {})
    mastery = None

    if target_topic and target_topic in topic_stats:
        mastery = topic_stats[target_topic].get("mastery", 0.0)

    if mastery is None:
        mastery = profile.overall_mastery

    if mastery < 0.4:
        return 1
    if mastery < 0.75:
        return 2
    return 3


def _difficulty_score(
    problem_difficulty: str | None,
    target_difficulty: str,
    explicit: bool,
) -> tuple[int, list[str]]:
    reasons: list[str] = []

    if not problem_difficulty:
        return 0, reasons

    if problem_difficulty == target_difficulty:
        if explicit:
            reasons.append(f"точно совпадает сложность '{target_difficulty}'")
            return 60, reasons
        reasons.append(f"подходит уровень сложности '{target_difficulty}'")
        return 15, reasons

    current_order = DIFFICULTY_ORDER.get(problem_difficulty, 2)
    target_order = DIFFICULTY_ORDER.get(target_difficulty, 2)

    if abs(current_order - target_order) == 1:
        reasons.append("уровень сложности близок к целевому")
        return (15 if explicit else 5), reasons

    return (-10 if explicit else 0), reasons


def _steps_score(
    problem_steps: int | None,
    target_steps: int,
    explicit: bool,
) -> tuple[int, list[str]]:
    reasons: list[str] = []

    if problem_steps is None:
        return 0, reasons

    if problem_steps == target_steps:
        if explicit:
            reasons.append(f"точно совпадает количество шагов '{target_steps}'")
            return 60, reasons
        reasons.append(f"подходит по количеству шагов '{target_steps}'")
        return 15, reasons

    if abs(problem_steps - target_steps) == 1:
        reasons.append("количество шагов близко к целевому")
        return (15 if explicit else 5), reasons

    return (-10 if explicit else 0), reasons


def _score_problem(
    problem: Problem,
    profile_key: str | None,
    explicit_topic: str | None,
    explicit_diagnosis: str | None,
    explicit_difficulty: str | None,
    explicit_max_steps: int | None,
    target_topic: str | None,
    target_diagnosis: str | None,
    target_difficulty: str,
    target_max_steps: int,
) -> tuple[int, list[str]]:
    metadata = dict(problem.metadata_json or {})
    reason_parts: list[str] = []
    score = 0

    profile_key_hint = metadata.get("profile_key_hint")
    if profile_key:
        if profile_key_hint == profile_key:
            score += 200
            reason_parts.append(f"помечена для профиля '{profile_key}'")
        elif profile_key_hint:
            score -= 40

    if explicit_topic:
        if problem.topic == explicit_topic:
            score += 120
            reason_parts.append(f"точно совпадает тема '{explicit_topic}'")
        else:
            score -= 30
    elif target_topic and problem.topic == target_topic:
        score += 60
        reason_parts.append(f"совпадает тема '{target_topic}'")

    focus_diagnosis = metadata.get("focus_diagnosis")
    if explicit_diagnosis:
        if focus_diagnosis == explicit_diagnosis:
            score += 120
            reason_parts.append(f"точно совпадает фокус ошибки '{explicit_diagnosis}'")
        elif focus_diagnosis:
            score -= 30
    elif target_diagnosis and focus_diagnosis == target_diagnosis:
        score += 35
        reason_parts.append(f"нацелена на ошибку '{target_diagnosis}'")

    difficulty = metadata.get("difficulty")
    diff_score, diff_reasons = _difficulty_score(
        problem_difficulty=difficulty,
        target_difficulty=target_difficulty,
        explicit=explicit_difficulty is not None,
    )
    score += diff_score
    reason_parts.extend(diff_reasons)

    max_steps = metadata.get("max_steps")
    step_score, step_reasons = _steps_score(
        problem_steps=max_steps,
        target_steps=target_max_steps,
        explicit=explicit_max_steps is not None,
    )
    score += step_score
    reason_parts.extend(step_reasons)

    if not metadata:
        score += 1
        reason_parts.append("задача без дополнительной разметки")

    return score, reason_parts


def choose_problem_with_filters(
    db: Session,
    profile_key: str | None = None,
    topic: str | None = None,
    difficulty: str | None = None,
    focus_diagnosis: str | None = None,
    max_steps: int | None = None,
) -> dict | None:
    profile = get_or_create_profile(db, profile_key=profile_key) if profile_key else None

    inferred_diagnosis = _pick_primary_diagnosis(profile) if profile else None
    inferred_topic = _pick_target_topic(profile, inferred_diagnosis) if profile else None
    inferred_difficulty = _pick_target_difficulty(profile, inferred_topic) if profile else "medium"
    inferred_max_steps = _pick_target_max_steps(profile, inferred_topic) if profile else 2

    target_diagnosis = focus_diagnosis or inferred_diagnosis
    target_topic = topic or inferred_topic
    target_difficulty = difficulty or inferred_difficulty
    target_max_steps = max_steps or inferred_max_steps

    problems = list(db.scalars(select(Problem)).all())
    if not problems:
        return None

    best_problem = None
    best_score = -10**9
    best_reasons: list[str] = []

    for problem in problems:
        score, reasons = _score_problem(
            problem=problem,
            profile_key=profile_key,
            explicit_topic=topic,
            explicit_diagnosis=focus_diagnosis,
            explicit_difficulty=difficulty,
            explicit_max_steps=max_steps,
            target_topic=target_topic,
            target_diagnosis=target_diagnosis,
            target_difficulty=target_difficulty,
            target_max_steps=target_max_steps,
        )

        if score > best_score:
            best_score = score
            best_problem = problem
            best_reasons = reasons

    if best_problem is None:
        return None

    reason = "Рекомендация выбрана автоматически."
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
        "target_max_steps": target_max_steps,
        "reason": reason,
    }


def choose_next_problem(db: Session, profile_key: str) -> dict | None:
    return choose_problem_with_filters(
        db=db,
        profile_key=profile_key,
    )
