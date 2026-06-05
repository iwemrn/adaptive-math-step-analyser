from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_create_attempt():
    problem_response = client.post(
        "/problems",
        json={
            "topic": "linear_equations",
            "title": "Уравнение для попытки",
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
    data = attempt_response.json()
    assert data["problem_id"] == problem_id
    assert data["status"] == "active"
    assert "id" in data
