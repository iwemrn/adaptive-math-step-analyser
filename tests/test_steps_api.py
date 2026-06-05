from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_submit_step():
    # 1. Создаём задачу
    problem_response = client.post(
        "/problems",
        json={
            "topic": "linear_equations",
            "title": "Проверка шага",
            "statement": "Решите уравнение 2x + 6 = 10",
            "expected_answer": "2"
        },
    )
    assert problem_response.status_code == 201
    problem_id = problem_response.json()["id"]

    # 2. Создаём попытку
    attempt_response = client.post(
        "/attempts",
        json={"problem_id": problem_id},
    )
    assert attempt_response.status_code == 201
    attempt_id = attempt_response.json()["id"]

    # 3. Отправляем шаг
    step_response = client.post(
        f"/attempts/{attempt_id}/steps",
        json={"raw_text": "2x + 6 = 10 => 2x = 4"},
    )

    assert step_response.status_code == 201
    data = step_response.json()

    assert data["step_order"] == 1
    assert data["raw_text"] == "2x + 6 = 10 => 2x = 4"
    assert data["is_valid"] is True
    assert data["soft_score"] == 0.8
    assert data["operation_type"] == "pending_analysis"
    assert data["feedback"]["type"] == "confirm"
