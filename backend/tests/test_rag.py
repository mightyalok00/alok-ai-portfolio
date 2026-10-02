from app.rag.retriever import retrieve


def test_retrieval():
    """WHY: Relevant evidence must be retrieved before generation."""
    docs = ["Python FastAPI project", "SQL patient flow project"]
    assert retrieve("Python FastAPI", docs)[0] == docs[0]
