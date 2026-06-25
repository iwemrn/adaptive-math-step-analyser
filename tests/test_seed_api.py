from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_seed_default_problems():
    response = client.post("/admin/seed-default-problems")
    assert response.status_code == 200

    data = response.json()

    assert "created" in data
    assert "skipped" in data
    assert "total_templates" in data
