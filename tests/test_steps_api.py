from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_submit_step_transition_valid():
    problem_response = client.post(
        "/problems",
        json={
            "topic": "linear_equations",
            "title": "Проверка корректного шага",
            "statement": "Решите уравнение 2x + 6 = 10",
            "expected_answer": "2"
        },
    )
    assert problem_response.status_code == 201
    problem_id = problem_response.json()["id"]

    attempt_response = client.post(
        "/attempts",
        json={"problem_id": problem_id},
    )
    assert attempt_response.status_code == 201
    attempt_id = attempt_response.json()["id"]

    step_response = client.post(
        f"/attempts/{attempt_id}/steps",
        json={"raw_text": "2x + 6 = 10 => 2x = 4"},
    )

    assert step_response.status_code == 201
    data = step_response.json()

    assert data["step_order"] == 1
    assert data["normalized_before"] == "2x + 6 = 10"
    assert data["normalized_after"] == "2x = 4"
    assert data["is_valid"] is True
    assert data["soft_score"] == 0.95
    assert data["operation_type"] == "equivalent_transition"
    assert data["diagnosis_code"] == "equivalent_transition"
    assert data["feedback"]["type"] == "confirm"


def test_submit_step_transition_sign_error():
    problem_response = client.post(
        "/problems",
        json={
            "topic": "linear_equations",
            "title": "Проверка ошибки знака",
            "statement": "Решите уравнение 2x + 6 = 10",
            "expected_answer": "2"
        },
    )
    assert problem_response.status_code == 201
    problem_id = problem_response.json()["id"]

    attempt_response = client.post(
        "/attempts",
        json={"problem_id": problem_id},
    )
    assert attempt_response.status_code == 201
    attempt_id = attempt_response.json()["id"]

    step_response = client.post(
        f"/attempts/{attempt_id}/steps",
        json={"raw_text": "2x + 6 = 10 => 2x = 16"},
    )

    assert step_response.status_code == 201
    data = step_response.json()

    assert data["is_valid"] is False
    assert data["operation_type"] == "invalid_transition"
    assert data["diagnosis_code"] == "sign_error"
    assert data["feedback"]["type"] == "explain_error"
    assert "sign_error" in data["error_probs"]


def test_submit_step_single_expression():
    problem_response = client.post(
        "/problems",
        json={
            "topic": "linear_equations",
            "title": "Одиночное выражение",
            "statement": "Решите уравнение x + 2 = 5",
            "expected_answer": "3"
        },
    )
    assert problem_response.status_code == 201
    problem_id = problem_response.json()["id"]

    attempt_response = client.post(
        "/attempts",
        json={"problem_id": problem_id},
    )
    assert attempt_response.status_code == 201
    attempt_id = attempt_response.json()["id"]

    step_response = client.post(
        f"/attempts/{attempt_id}/steps",
        json={"raw_text": "x = 3"},
    )

    assert step_response.status_code == 201
    data = step_response.json()

    assert data["normalized_before"] is None
    assert data["normalized_after"] == "x = 3"
    assert data["operation_type"] == "single_expression"
    assert data["diagnosis_code"] == "single_expression"
    assert data["feedback"]["type"] == "hint"
