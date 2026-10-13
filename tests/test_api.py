"""FastAPI endpoint smoke and security regression tests."""
from fastapi.testclient import TestClient

from agents.api import app


def test_api_health_audit_metrics_and_log():
    client = TestClient(app)
    assert client.get("/health").status_code == 200
    data = client.post("/api/audit", json={
        "task_id": "DEMO-API-01",
        "target_identifier": "SPECIMEN-A",
        "primary_metric": 26.0,
        "secondary_metric": 2.0,
        "status_descriptor": "NOMINAL",
        "is_critical_flag": False
    })
    assert data.status_code == 200
    payload = data.json()
    assert payload["overall_urgency"] == "ELEVATED_RISK"
    assert payload["total_alerts"] == 1
    assert client.get("/metrics").json()["dossiers_processed_total"] >= 1
    trail = client.get("/api/audit/logs")
    assert trail.status_code == 200
    assert trail.json()["verified"] is True


def test_api_rejects_identifiers_without_echoing_input():
    client = TestClient(app)
    response = client.post("/api/audit", json={
        "task_id": "PATIENT-MRN-123456",
        "target_identifier": "SAMPLE-A",
        "primary_metric": 1.0
    })
    assert response.status_code == 422
    assert "123456" not in response.text

    answer = client.post("/api/chat", json={"query": "Email me at patient@example.com"})
    assert answer.status_code == 422
    assert "patient@example.com" not in answer.text


def test_api_rejects_non_finite_numbers():
    client = TestClient(app)
    response = client.post("/api/audit", json={
        "task_id": "DEMO-API-02",
        "target_identifier": "SAMPLE-A",
        "primary_metric": "NaN"
    })
    assert response.status_code == 422
