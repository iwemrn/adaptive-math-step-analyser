from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_reset_profile_route():
    profile_key = "reset_demo_student"

    profile_response = client.get(f"/profiles/{profile_key}")
    assert profile_response.status_code == 200

    problem_response = client.post(
        "/problems",
        json={
            "topic": "linear_equations",
            "title": "Профиль для сброса",
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
        f"/attempts/{attempt_id}/steps?profile_key={profile_key}",
        json={"raw_text": "2x + 6 = 10 => 2x = 16"},
    )
    assert step_response.status_code == 201

    reset_response = client.post(f"/admin/profiles/{profile_key}/reset")
    assert reset_response.status_code == 200
    assert reset_response.json()["status"] == "reset"

    after_response = client.get(f"/profiles/{profile_key}")
    assert after_response.status_code == 200
    after_data = after_response.json()

    assert after_data["total_steps"] == 0
    assert after_data["incorrect_steps"] == 0
    assert after_data["misconception_stats_json"] == {}
