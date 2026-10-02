from app.candidate import load_candidate
from app.jd_matcher import build_job_match


def test_jd_matcher_uses_documented_evidence_only():
    """WHY: JD matching must not depend on Ollama output formatting."""
    candidate = load_candidate()
    result = build_job_match(
        candidate,
        """
        Requirements:
        - Python
        - Pandas and NumPy
        - Scikit-learn
        - Machine learning
        - Regression and classification
        - SQL
        - Data visualization
        - Model evaluation
        - TensorFlow
        - 3+ years experience
        """,
    )

    assert "Python" in result["matched_documented_skills"]
    assert "Pandas" in result["matched_documented_skills"]
    assert "NumPy" in result["matched_documented_skills"]
    assert "Scikit-learn" in result["matched_documented_skills"]
    assert "SQL" in result["matched_documented_skills"]
    assert any(
        item.startswith("Data visualization")
        for item in result["matched_documented_skills"]
    )
    assert any(
        "tensorflow" in item.lower()
        for item in result["requested_but_not_verified"]
    )
    assert any(
        "employment experience" in item.lower()
        for item in result["requested_but_not_verified"]
    )


def test_jd_matcher_never_calls_an_llm():
    """WHY: A deterministic analyzer cannot fail because a model emits invalid JSON."""
    candidate = load_candidate()
    result = build_job_match(candidate, "Python, SQL, and FastAPI")

    assert result["matched_documented_skills"] == [
        "Python",
        "FastAPI",
        "SQL",
    ]
    assert result["relevant_projects"]


def test_match_job_api_returns_structured_json():
    """WHY: The frontend must receive valid structured JSON without Ollama."""
    from fastapi.testclient import TestClient
    from app.main import app

    response = TestClient(app).post(
        "/api/match-job",
        json={
            "job_description": (
                "Python, Pandas, NumPy, Scikit-learn, SQL, "
                "and Generative AI."
            )
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert "Python" in payload["matched_documented_skills"]
    assert "Pandas" in payload["matched_documented_skills"]
    assert "relevant_projects" in payload
    assert "requested_but_not_verified" in payload
