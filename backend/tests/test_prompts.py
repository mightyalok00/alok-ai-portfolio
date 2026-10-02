from app.prompts import build_jd_context


def test_jd_context_treats_analyzer_as_authoritative():
    """WHY: The LLM must explain deterministic analyzer results, not reclassify them."""
    context = build_jd_context({
        "job_description": "Python and machine learning role",
        "matched_documented_skills": ["Python", "Machine Learning"],
        "relevant_projects": ["Gradient Descent Mastery"],
        "requested_but_not_verified": [],
        "evidence": ["Gradient Descent Mastery documents Python and regression work."],
        "notes": [],
    })

    assert "DOCUMENTED MATCHES:" in context
    assert "Python, Machine Learning" in context
    assert "RELEVANT PROJECTS:" in context
    assert "Gradient Descent Mastery" in context
    assert "NONE — the analyzer flagged no requirements as not verified." in context
    assert "requested_but_not_verified is the ONLY list" in context


def test_jd_context_only_allows_explicit_unverified_items():
    """WHY: Model output must never invent a verification gap from the JD wording."""
    context = build_jd_context({
        "job_description": "Python and TensorFlow role",
        "matched_documented_skills": ["Python"],
        "relevant_projects": ["Project A"],
        "requested_but_not_verified": ["TensorFlow"],
        "evidence": [],
        "notes": [],
    })

    assert "NOT VERIFIED:\nTensorFlow" in context
    assert "Do not infer, speculate, or create additional verification gaps" in context
