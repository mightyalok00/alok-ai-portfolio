from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    """WHY: Health endpoint is the first local diagnostic."""
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["provider"] == "ollama"


def test_candidate():
    """WHY: Frontend needs a stable candidate endpoint."""
    assert client.get("/api/candidate").json()["name"] == "Alok Agarwal"
