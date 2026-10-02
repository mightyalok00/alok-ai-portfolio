from app.candidate import load_candidate


def test_candidate():
    """WHY: Validate the portfolio source of truth at test time."""
    c = load_candidate()
    assert c.name == "Alok Agarwal"
    assert len(c.projects) >= 10
