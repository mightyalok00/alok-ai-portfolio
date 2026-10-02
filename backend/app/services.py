import json
from collections.abc import Iterator

from app.candidate import load_candidate
from app.llm.router import ModelRouter
from app.prompts import SYSTEM_PROMPT, build_context
from app.rag.documents import load_documents
from app.rag.retriever import retrieve


class PortfolioService:
    """Application service for grounded recruiter portfolio workflows."""

    def __init__(self) -> None:
        self.candidate = load_candidate()
        self.documents = load_documents("data/documents")
        self.router = ModelRouter()

    def _candidate_json(self) -> str:
        """Serialize validated candidate evidence for model context."""
        return json.dumps(
            self.candidate.model_dump(),
            ensure_ascii=False,
            indent=2,
        )

    def stream_chat(self, message: str, history: list[dict]) -> Iterator[str]:
        """Stream a grounded answer with retrieved portfolio evidence."""
        retrieved = retrieve(message, self.documents)
        history_text = "\n".join(
            f"{item['role'].upper()}: {item['content']}"
            for item in history[-8:]
        )
        prompt = f"""
{build_context(self._candidate_json(), retrieved)}

RECENT CONVERSATION:
{history_text or "No previous conversation."}

RECRUITER QUESTION:
{message}
"""
        yield from self.router.provider_for(message).stream(SYSTEM_PROMPT, prompt)

    def match_job(self, job_description: str) -> str:
        """Return structured JD analysis without a hiring verdict."""
        retrieved = retrieve(job_description, self.documents, top_k=8)
        prompt = f"""
Analyze this job description against documented portfolio evidence.

Return ONLY valid JSON:
{{
  "matched_documented_skills": [],
  "relevant_projects": [],
  "evidence": [],
  "requested_but_not_verified": [],
  "notes": []
}}

Rules:
- Do not assign a hiring score.
- Do not recommend hiring or rejection.
- Do not claim a missing skill is absent; call it "not verified".
- Every evidence item must be supported by the supplied candidate/project data.

CANDIDATE:
{self._candidate_json()}

RETRIEVED EVIDENCE:
{"\n\n".join(retrieved) or "No matching evidence was retrieved."}

JOB DESCRIPTION:
{job_description}
"""
        return self.router.provider_for(
            "job description requirements analysis compare match"
        ).generate(SYSTEM_PROMPT, prompt)

    def interview(self, focus: str, previous_answer: str, history: list[dict]) -> str:
        """Generate an evidence-grounded technical interview coaching turn."""
        retrieved = retrieve(f"{focus} {previous_answer}", self.documents, top_k=5)
        prompt = f"""
Act as a portfolio interview coach.

Create a realistic technical interview turn based only on documented portfolio evidence.

Return ONLY valid JSON:
{{
  "question": "...",
  "why_it_matters": "...",
  "evaluation": "...",
  "follow_up": "...",
  "evidence": []
}}

If no previous answer exists, evaluation should explain what a strong answer should
cover rather than pretending to evaluate an answer.

FOCUS:
{focus}

PREVIOUS ANSWER:
{previous_answer or "None"}

CANDIDATE:
{self._candidate_json()}

EVIDENCE:
{"\n\n".join(retrieved) or "No specific project evidence was retrieved."}
"""
        return self.router.provider_for(
            "interview reasoning analysis"
        ).generate(SYSTEM_PROMPT, prompt)
