from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_projects_endpoint():
    """WHY: The portfolio UI needs structured project cards independent of chat."""
    response = client.get("/api/projects")
    assert response.status_code == 200
    assert response.json()


def test_health_reports_evidence_counts():
    """WHY: Local diagnostics should reveal whether the knowledge base loaded."""
    response = client.get("/api/health")
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["projects"] > 0
    assert payload["documents"] >= 0
