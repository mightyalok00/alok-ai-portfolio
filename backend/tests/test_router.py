from app.llm.router import ModelRouter


def test_general():
    """WHY: General questions should use the lightweight conversational model."""
    assert ModelRouter().choose_model("Tell me about Alok") == "llama3.2:latest"


def test_code():
    """WHY: Technical questions should use the coding model."""
    assert ModelRouter().choose_model("Explain the Python FastAPI architecture") == "qwen2.5-coder:7b"


def test_reasoning():
    """WHY: JD analysis should use the reasoning model."""
    assert ModelRouter().choose_model("Analyze this job description") == "deepseek-r1:7b"
