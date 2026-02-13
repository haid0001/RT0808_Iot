import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_create_runner():
    response = client.post("/api/runners", json={
        "name": "Test",
        "email": "test@test.com"
    })
    assert response.status_code == 200
    assert "id" in response.json()

def test_invalid_gps():
    response = client.post("/api/measurements", json={
        "session_id": 1,
        "lat": 200,
        "lon": 2,
        "battery": 50,
        "temperature": 20
    })
    assert "error" in response.json()
def test_end_to_end_flow():

    # Create runner
    runner = client.post("/api/runners", json={
        "name": "E2E",
        "email": "e2e@test.com"
    }).json()

    # Create session
    session = client.post("/api/sessions", json={
        "runner_id": runner["id"]
    }).json()

    # Poll sensor (avec clé auth)
    response = client.post(
        f"/api/poll/{session['id']}",
        headers={"x-device-key": "THREAD_SECRET_2026"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "measurement_id" in data
