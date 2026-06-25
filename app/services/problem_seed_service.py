from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.problem import Problem


DEFAULT_PROBLEMS = [
    {
        "topic": "linear_equations",
        "title": "Перенос слагаемого 1",
        "statement": "Решите уравнение 2x + 6 = 10",
        "expected_answer": "2",
        "metadata_json": {
            "difficulty": "easy",
            "focus_diagnosis": "sign_error",
            "max_steps": 2,
        },
    },
    {
        "topic": "linear_equations",
        "title": "Перенос слагаемого 2",
        "statement": "Решите уравнение 3x - 5 = 16",
        "expected_answer": "7",
        "metadata_json": {
            "difficulty": "easy",
            "focus_diagnosis": "sign_error",
            "max_steps": 2,
        },
    },
    {
        "topic": "linear_equations",
        "title": "Деление обеих частей",
        "statement": "Решите уравнение 4x = 20",
        "expected_answer": "5",
        "metadata_json": {
            "difficulty": "easy",
            "focus_diagnosis": "arithmetic_error",
            "max_steps": 1,
        },
    },
    {
        "topic": "linear_equations",
        "title": "Линейное уравнение средней сложности",
        "statement": "Решите уравнение 5x + 8 = 3x + 18",
        "expected_answer": "5",
        "metadata_json": {
            "difficulty": "medium",
            "focus_diagnosis": "invalid_transform",
            "max_steps": 3,
        },
    },
    {
        "topic": "fractions",
        "title": "Потеря ОДЗ в дроби",
        "statement": "Решите уравнение (x^2 - 1)/(x - 1) = 2",
        "expected_answer": "нет решений",
        "metadata_json": {
            "difficulty": "medium",
            "focus_diagnosis": "possible_domain_loss",
            "max_steps": 2,
        },
    },
    {
        "topic": "fractions",
        "title": "Знаменатель и ОДЗ",
        "statement": "Решите уравнение (x + 2)/(x - 3) = 1",
        "expected_answer": "нет решений",
        "metadata_json": {
            "difficulty": "medium",
            "focus_diagnosis": "division_by_zero",
            "max_steps": 2,
        },
    },
]


def seed_default_problems(db: Session) -> dict:
    created = 0
    skipped = 0

    existing_titles = set(
        db.scalars(select(Problem.title)).all()
    )

    for item in DEFAULT_PROBLEMS:
        if item["title"] in existing_titles:
            skipped += 1
            continue

        problem = Problem(
            topic=item["topic"],
            title=item["title"],
            statement=item["statement"],
            expected_answer=item["expected_answer"],
            metadata_json=item["metadata_json"],
        )
        db.add(problem)
        created += 1

    db.commit()

    return {
        "created": created,
        "skipped": skipped,
        "total_templates": len(DEFAULT_PROBLEMS),
    }
