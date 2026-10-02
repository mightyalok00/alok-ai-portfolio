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


def test_interview_request_accepts_active_jd_context():
    """WHY: Interview Mode must be able to consume the same deterministic JD session."""
    request = InterviewRequest(
        focus="Python",
        jd_context={
            "job_description": "Python Data Scientist with Pandas and FastAPI experience.",
            "matched_documented_skills": ["Python", "Pandas", "FastAPI"],
            "relevant_projects": ["Example Project"],
            "requested_but_not_verified": [],
            "evidence": ["Python — documented in 1 project(s): Example Project"],
            "notes": ["Matches are based only on documented candidate/project data."],
        },
    )
    assert request.jd_context is not None
    assert request.jd_context.matched_documented_skills == ["Python", "Pandas", "FastAPI"]
