from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_generate_problem_with_explicit_filters():
    target_response = client.post(
        "/problems",
        json={
            "topic": "custom_topic_alpha",
            "title": "Целевая задача",
            "statement": "Решите уравнение x + 7 = 12",
            "expected_answer": "5",
            "metadata_json": {
                "difficulty": "easy",
                "focus_diagnosis": "sign_error"
            }
        },
    )
    assert target_response.status_code == 201
    target_problem_id = target_response.json()["id"]

    other_response = client.post(
        "/problems",
        json={
            "topic": "custom_topic_beta",
            "title": "Другая задача",
            "statement": "Решите уравнение 3x = 9",
            "expected_answer": "3",
            "metadata_json": {
                "difficulty": "hard",
                "focus_diagnosis": "invalid_transform"
            }
        },
    )
    assert other_response.status_code == 201

    response = client.post(
        "/practice/generate-problem",
        json={
            "profile_key": "test_student",
            "topic": "custom_topic_alpha",
            "difficulty": "easy",
            "focus_diagnosis": "sign_error"
        },
    )
    assert response.status_code == 200

    data = response.json()
    assert data["problem_id"] == target_problem_id
    assert data["topic"] == "custom_topic_alpha"
    assert data["target_topic"] == "custom_topic_alpha"
    assert data["target_difficulty"] == "easy"
    assert data["based_on_diagnosis"] == "sign_error"


def test_generate_problem_uses_profile_when_filters_missing():
    profile_key = "generated_from_profile"

    target_response = client.post(
        "/problems",
        json={
            "topic": "linear_equations",
            "title": "Задача для профиля",
            "statement": "Решите уравнение 5x + 4 = 19",
            "expected_answer": "3",
            "metadata_json": {
                "difficulty": "easy",
                "focus_diagnosis": "sign_error",
                "profile_key_hint": profile_key
            }
        },
    )
    assert target_response.status_code == 201
    target_problem_id = target_response.json()["id"]

    source_problem_response = client.post(
        "/problems",
        json={
            "topic": "linear_equations",
            "title": "Исходная проблемная задача",
            "statement": "Решите уравнение 2x + 6 = 10",
            "expected_answer": "2",
            "metadata_json": {
                "difficulty": "easy",
                "focus_diagnosis": "sign_error"
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
    assert data["based_on_diagnosis"] == "sign_error"
    assert data["target_topic"] == "linear_equations"
