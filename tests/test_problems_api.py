from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_create_problem():
    response = client.post(
        "/problems",
        json={
            "topic": "linear_equations",
            "title": "Простое уравнение",
            "statement": "Решите уравнение 2x + 6 = 10",
            "expected_answer": "2"
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["topic"] == "linear_equations"
    assert data["title"] == "Простое уравнение"
    assert data["expected_answer"] == "2"
    assert "id" in data
