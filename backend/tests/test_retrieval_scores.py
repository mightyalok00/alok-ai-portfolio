from app.rag.retriever import retrieve_with_scores


def test_retrieval_is_ranked():
    """WHY: Evidence ranking must be deterministic enough to test locally."""
    docs = [
        "# Python\nPython FastAPI Pandas",
        "# SQL\nSQL patient flow",
    ]
    ranked = retrieve_with_scores("Python FastAPI", docs)
    assert ranked
    assert "FastAPI" in ranked[0][1]
    assert ranked[0][0] > 0
