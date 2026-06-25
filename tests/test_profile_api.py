from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_profile_updates_after_incorrect_step():
    before_response = client.get("/profiles/demo")
    assert before_response.status_code == 200
    before_data = before_response.json()

    before_total_steps = before_data["total_steps"]
    before_incorrect_steps = before_data["incorrect_steps"]
    before_topic_total = before_data["topic_mastery_json"].get("linear_equations", {}).get("total_steps", 0)
    before_sign_error = before_data["misconception_stats_json"].get("sign_error", 0)

    problem_response = client.post(
        "/problems",
        json={
            "topic": "linear_equations",
            "title": "Ошибка знака для профиля",
            "statement": "Решите уравнение 2x + 6 = 10",
            "expected_answer": "2",
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

    after_response = client.get("/profiles/demo")
    assert after_response.status_code == 200
    after_data = after_response.json()

    assert after_data["total_steps"] == before_total_steps + 1
    assert after_data["incorrect_steps"] == before_incorrect_steps + 1
    assert after_data["topic_mastery_json"]["linear_equations"]["total_steps"] == before_topic_total + 1
    assert after_data["misconception_stats_json"].get("sign_error", 0) == before_sign_error + 1
    assert isinstance(after_data["recommendations"], list)
    assert len(after_data["recommendations"]) >= 1
