import re
from collections.abc import Iterable

from app.models import Candidate

SKILL_ALIASES = {
    "Python": ("python",),
    "Pandas": ("pandas",),
    "NumPy": ("numpy",),
    "SciPy": ("scipy",),
    "Scikit-learn": ("scikit-learn", "scikit learn", "sklearn"),
    "Matplotlib": ("matplotlib",),
    "Seaborn": ("seaborn",),
    "Plotly": ("plotly",),
    "Streamlit": ("streamlit",),
    "FastAPI": ("fastapi", "fast api"),
    "SQL": ("sql", "structured query language"),
    "Machine Learning": ("machine learning", "ml"),
    "Regression": ("regression",),
    "Classification": ("classification",),
    "Model Evaluation": (
        "model evaluation",
        "model evaluation metrics",
        "model validation",
    ),
    "Generative AI": ("generative ai", "genai", "gen ai"),
    "GitHub": ("github",),
}

UNVERIFIED_TERMS = (
    "tensorflow",
    "pytorch",
    "keras",
    "xgboost",
    "lightgbm",
    "spark",
    "pyspark",
    "hadoop",
    "tableau",
    "power bi",
    "powerbi",
    "airflow",
    "docker",
    "kubernetes",
    "aws",
    "azure",
    "gcp",
    "google cloud",
    "databricks",
    "snowflake",
    "java",
    "c++",
    "c#",
    "javascript",
    "typescript",
    "react",
    "node.js",
    "nlp",
    "natural language processing",
)

VISUALIZATION_SKILLS = ("Matplotlib", "Seaborn", "Plotly")

QUESTION_STARTERS = (
    "what ", "which ", "how ", "why ", "when ", "where ",
    "who ", "can ", "could ", "would ", "should ", "is ", "are ",
    "do ", "does ", "did ", "will ",
)


def looks_like_question(value: str) -> bool:
    """Detect likely recruiter questions accidentally entered as a JD."""
    text = value.strip().lower()
    if not text:
        return False
    if text.endswith("?"):
        return True
    return text.startswith(QUESTION_STARTERS)


def normalize_text(value: str) -> str:
    """Normalize text for deterministic, case-insensitive phrase matching."""
    value = value.lower().replace("–", "-").replace("—", "-")
    value = re.sub(r"[^a-z0-9+#.\-]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def contains_phrase(text: str, phrase: str) -> bool:
    """Return whether a normalized phrase occurs as a whole phrase."""
    normalized_phrase = normalize_text(phrase)
    pattern = rf"(?<![a-z0-9]){re.escape(normalized_phrase)}(?![a-z0-9])"
    return re.search(pattern, text) is not None


def _unique(items: Iterable[str]) -> list[str]:
    """Preserve order while removing duplicate strings."""
    return list(dict.fromkeys(item for item in items if item))


def _project_evidence_count(project, canonical_skill: str) -> int:
    """Count project evidence supporting a documented skill."""
    aliases = SKILL_ALIASES.get(canonical_skill, (canonical_skill,))
    technologies = [normalize_text(item) for item in project.technologies]

    if any(
        normalize_text(canonical_skill) == tech
        or any(contains_phrase(tech, alias) for alias in aliases)
        for tech in technologies
    ):
        return 1

    searchable = normalize_text(
        f"{project.name} {project.description} "
        f"{' '.join(project.technologies)}"
    )
    return int(any(contains_phrase(searchable, alias) for alias in aliases))


def _relevant_projects(
    candidate: Candidate,
    matched_skills: list[str],
) -> list[str]:
    """Rank projects using only documented skill/project evidence."""
    scored: list[tuple[int, str]] = []

    for project in candidate.projects:
        score = sum(
            _project_evidence_count(project, skill)
            for skill in matched_skills
            if skill in SKILL_ALIASES
        )
        if score:
            scored.append((score, project.name))

    scored.sort(key=lambda item: (-item[0], item[1].lower()))
    return [name for _, name in scored[:6]]


def _requirement_lines(job_description: str) -> list[str]:
    """Extract human-readable requirement lines for conservative gap reporting."""
    lines = []

    for raw_line in job_description.splitlines():
        line = re.sub(r"^\s*[-*•\d.)]+\s*", "", raw_line).strip()
        if len(line) >= 4:
            lines.append(line)

    return _unique(lines)


def build_job_match(
    candidate: Candidate,
    job_description: str,
) -> dict[str, list[str]]:
    """Match a JD against the candidate source of truth without an LLM."""
    normalized_jd = normalize_text(job_description)
    matched: list[str] = []

    for skill in candidate.skills:
        aliases = SKILL_ALIASES.get(skill, (skill,))
        if any(contains_phrase(normalized_jd, alias) for alias in aliases):
            matched.append(skill)

    if contains_phrase(normalized_jd, "data visualization"):
        available = [
            skill for skill in VISUALIZATION_SKILLS
            if skill in candidate.skills
        ]
        if available:
            matched.append(
                "Data visualization — documented via "
                + ", ".join(available)
            )

    matched = _unique(matched)

    relevant = _relevant_projects(
        candidate,
        [skill for skill in matched if skill in SKILL_ALIASES],
    )

    evidence: list[str] = []

    for skill in matched:
        if skill.startswith("Data visualization"):
            evidence.append(skill)
            continue

        projects = [
            project.name
            for project in candidate.projects
            if _project_evidence_count(project, skill)
        ]

        if projects:
            evidence.append(
                f"{skill} — documented in {len(projects)} project(s): "
                + ", ".join(projects[:4])
            )
        else:
            evidence.append(
                f"{skill} — documented as a portfolio skill."
            )

    not_verified: list[str] = []

    for term in UNVERIFIED_TERMS:
        if contains_phrase(normalized_jd, term):
            not_verified.append(
                f"{term} — not verified in the portfolio data."
            )

    has_years = re.search(
        r"\b(?:\d+\+?|several|multiple)\s*(?:years?|yrs?)\b",
        normalized_jd,
    )

    if has_years and not candidate.experience:
        not_verified.append(
            "Employment experience — the candidate profile does not contain "
            "verified employment history."
        )

    if re.search(
        r"\b(?:bachelor|master|phd|degree|b\.?tech|m\.?tech|bsc|msc|mba)\b",
        normalized_jd,
    ) and not candidate.education:
        not_verified.append(
            "Education requirement — education records are not documented."
        )

    if re.search(
        r"\b(?:certification|certified|certificate)\b",
        normalized_jd,
    ) and not candidate.certifications:
        not_verified.append(
            "Certification requirement — certifications are not documented."
        )

    if re.search(
        r"\b(?:experience|professional|industry)\b",
        normalized_jd,
    ) and not candidate.experience:
        evidence.append(
            "Employment history is not documented; project evidence should "
            "not be interpreted as employment experience."
        )

    notes = [
        "Matches are based only on the documented candidate/project data.",
        "The analyzer does not make a hiring recommendation or score.",
    ]

    if not matched and _requirement_lines(job_description):
        notes.append(
            "No documented skill phrase matched directly. Review the "
            "requested requirements against the portfolio evidence."
        )

    return {
        "matched_documented_skills": matched,
        "relevant_projects": relevant,
        "evidence": _unique(evidence),
        "requested_but_not_verified": _unique(not_verified),
        "notes": notes,
    }
