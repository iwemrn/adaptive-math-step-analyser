from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_next_problem_recommendation_for_sign_error_profile():
    profile_key = "next_problem_student"

    target_problem_response = client.post(
        "/problems",
        json={
            "topic": "linear_equations",
            "title": "Тренировка переноса слагаемых",
            "statement": "Решите уравнение 3x + 5 = 14",
            "expected_answer": "3",
            "metadata_json": {
                "difficulty": "easy",
                "focus_diagnosis": "sign_error"
            }
        },
    )
    assert target_problem_response.status_code == 201
    target_problem_id = target_problem_response.json()["id"]

    other_problem_response = client.post(
        "/problems",
        json={
            "topic": "fractions",
            "title": "ОДЗ в дробях",
            "statement": "Решите уравнение (x^2 - 4)/(x - 2) = 3",
            "expected_answer": "нет решений",
            "metadata_json": {
                "difficulty": "medium",
                "focus_diagnosis": "possible_domain_loss"
            }
        },
    )
    assert other_problem_response.status_code == 201

    source_problem_response = client.post(
        "/problems",
        json={
            "topic": "linear_equations",
            "title": "Проблемная задача",
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

    recommendation_response = client.get(f"/practice/next-problem/{profile_key}")
    assert recommendation_response.status_code == 200

    data = recommendation_response.json()

    assert data["problem_id"] == target_problem_id
    assert data["topic"] == "linear_equations"
    assert data["based_on_diagnosis"] == "sign_error"
    assert data["target_topic"] == "linear_equations"
    assert data["target_difficulty"] in ["easy", "medium", "hard"]
    assert "reason" in data
