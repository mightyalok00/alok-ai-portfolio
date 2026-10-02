from app.candidate import load_candidate


def test_unverified_personal_fields_remain_empty():
    """WHY: Empty unsupported fields prevent the model from inventing personal facts."""
    candidate = load_candidate()
    assert candidate.education == []
    assert candidate.experience == []
    assert candidate.certifications == []
    assert candidate.achievements == []
    assert candidate.social_links["linkedin"] is None
