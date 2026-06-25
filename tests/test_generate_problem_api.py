from uuid import uuid4

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_generate_problem_with_explicit_filters():
    suffix = uuid4().hex[:8]
    profile_key = f"test_student_{suffix}"
    target_topic = f"custom_topic_alpha_{suffix}"
    target_title = f"Целевая задача {suffix}"
    other_topic = f"custom_topic_beta_{suffix}"

    target_response = client.post(
        "/problems",
        json={
            "topic": target_topic,
            "title": target_title,
            "statement": "Решите уравнение x + 7 = 12",
            "expected_answer": "5",
            "metadata_json": {
                "difficulty": "easy",
                "focus_diagnosis": "sign_error",
                "max_steps": 1,
                "profile_key_hint": profile_key,
            }
        },
    )
    assert target_response.status_code == 201
    target_problem = target_response.json()
    target_problem_id = target_problem["id"]

    other_response = client.post(
        "/problems",
        json={
            "topic": other_topic,
            "title": f"Другая задача {suffix}",
            "statement": "Решите уравнение 3x = 9",
            "expected_answer": "3",
            "metadata_json": {
                "difficulty": "hard",
                "focus_diagnosis": "invalid_transform",
                "max_steps": 3
            }
        },
    )
    assert other_response.status_code == 201

    response = client.post(
        "/practice/generate-problem",
        json={
            "profile_key": profile_key,
            "topic": target_topic,
            "difficulty": "easy",
            "focus_diagnosis": "sign_error",
            "max_steps": 1
        },
    )
    assert response.status_code == 200

    data = response.json()
    assert data["problem_id"] == target_problem_id
    assert data["topic"] == target_topic
    assert data["title"] == target_title
    assert data["target_topic"] == target_topic
    assert data["target_difficulty"] == "easy"
    assert data["target_max_steps"] == 1
    assert data["based_on_diagnosis"] == "sign_error"


def test_generate_problem_uses_profile_when_filters_missing():
    suffix = uuid4().hex[:8]
    profile_key = f"generated_from_profile_{suffix}"
    target_topic = f"linear_equations_{suffix}"
    target_title = f"Задача для профиля {suffix}"

    target_response = client.post(
        "/problems",
        json={
            "topic": target_topic,
            "title": target_title,
            "statement": "Решите уравнение 5x + 4 = 19",
            "expected_answer": "3",
            "metadata_json": {
                "difficulty": "easy",
                "focus_diagnosis": "sign_error",
                "profile_key_hint": profile_key,
                "max_steps": 1
            }
        },
    )
    assert target_response.status_code == 201
    target_problem = target_response.json()
    target_problem_id = target_problem["id"]

    source_problem_response = client.post(
        "/problems",
        json={
            "topic": target_topic,
            "title": f"Исходная проблемная задача {suffix}",
            "statement": "Решите уравнение 2x + 6 = 10",
            "expected_answer": "2",
            "metadata_json": {
                "difficulty": "easy",
                "focus_diagnosis": "sign_error",
                "max_steps": 2
            }
        },
    )
    assert source_problem_response.status_code == 201
    source_problem_id = source_problem_response.json()["id"]

    attempt_response = client.post(
        "/attempts",
        json={"problem_id": source_problem_id},
    )
    assert attempt_response.status_code == 201
    attempt_id = attempt_response.json()["id"]

    step_response = client.post(
        f"/attempts/{attempt_id}/steps?profile_key={profile_key}",
        json={"raw_text": "2x + 6 = 10 => 2x = 16"},
    )
    assert step_response.status_code == 201

    response = client.post(
        "/practice/generate-problem",
        json={
            "profile_key": profile_key
        },
    )
    assert response.status_code == 200

    data = response.json()
    assert data["problem_id"] == target_problem_id
    assert data["title"] == target_title
    assert data["based_on_diagnosis"] == "sign_error"
    assert data["target_topic"] == target_topic
    assert data["target_max_steps"] in [1, 2, 3]
