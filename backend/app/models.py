from typing import Literal

from pydantic import BaseModel, Field


class Project(BaseModel):
    """A documented portfolio project."""

    name: str
    description: str
    technologies: list[str] = Field(default_factory=list)
    repository: str | None = None
    demo: str | None = None
    evidence_notes: list[str] = Field(default_factory=list)


class Candidate(BaseModel):
    """Validated candidate profile used as the portfolio source of truth."""

    name: str
    headline: str
    summary: str
    location: str | None = None
    education: list[dict] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)
    experience: list[dict] = Field(default_factory=list)
    achievements: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    social_links: dict[str, str | None] = Field(default_factory=dict)
    data_notes: list[str] = Field(default_factory=list)


class ChatMessage(BaseModel):
    """One message in a recruiter conversation."""

    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    """Chat request containing the question and recent conversation history."""

    message: str = Field(min_length=1, max_length=4000)
    history: list[ChatMessage] = Field(default_factory=list)


class JobMatchRequest(BaseModel):
    """Job description submitted for evidence-based analysis."""

    job_description: str = Field(min_length=20, max_length=15000)


class JobMatchResponse(BaseModel):
    """Structured, non-ranking job-description analysis."""

    matched_documented_skills: list[str]
    relevant_projects: list[str]
    evidence: list[str]
    requested_but_not_verified: list[str]
    notes: list[str]


class InterviewRequest(BaseModel):
    """Request for the next portfolio interview question."""

    focus: str = Field(default="machine learning", max_length=300)
    previous_answer: str = Field(default="", max_length=6000)
    history: list[ChatMessage] = Field(default_factory=list)


class InterviewResponse(BaseModel):
    """Structured interview coaching response."""

    question: str
    why_it_matters: str
    evaluation: str
    follow_up: str
    evidence: list[str]


class Source(BaseModel):
    """A portfolio evidence source displayed to the frontend."""

    title: str
    url: str | None = None
    type: str = "portfolio"
