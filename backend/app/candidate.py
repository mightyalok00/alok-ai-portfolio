import json
from pathlib import Path
from app.config import settings
from app.models import Candidate


def load_candidate() -> Candidate:
    """WHY: Load the exact evidence file used by the API and validate it with Pydantic."""
    path = Path(settings.candidate_path)
    if not path.is_absolute():
        path = Path(__file__).resolve().parents[1] / path
    return Candidate.model_validate(json.loads(path.read_text(encoding="utf-8")))
