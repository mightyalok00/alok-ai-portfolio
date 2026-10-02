import json
from collections.abc import Iterator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from app.config import settings
from app.models import ChatRequest, InterviewRequest, JobMatchRequest, JobMatchResponse
from app.services import PortfolioService
from app.jd_matcher import looks_like_question

app = FastAPI(
    title="Alok AI Portfolio API",
    version="2.0.0",
    description="Local Ollama-powered recruiter portfolio API.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

service = PortfolioService()


@app.get("/api/health")
def health() -> dict:
    """Return API status plus a real Ollama connectivity check."""
    ollama_status = service.router.provider_for("health check").health()
    return {
        "status": "ok",
        "provider": "ollama",
        "ollama_status": ollama_status,
        "ollama_base_url": settings.ollama_base_url,
        "models": {
            "general": settings.ollama_chat_model,
            "technical": settings.ollama_code_model,
            "reasoning": settings.ollama_reasoning_model,
        },
        "projects": len(service.candidate.projects),
        "documents": len(service.documents),
    }


@app.get("/api/candidate")
def candidate() -> dict:
    """Return public portfolio data."""
    return service.candidate.model_dump()


@app.get("/api/projects")
def projects() -> list[dict]:
    """Return project cards for the portfolio explorer."""
    return [project.model_dump() for project in service.candidate.projects]


@app.post("/api/chat")
def chat(request: ChatRequest) -> StreamingResponse:
    """Stream an evidence-grounded recruiter response."""
    history = [message.model_dump() for message in request.history]

    def event_stream() -> Iterator[str]:
        try:
            for chunk in service.stream_chat(
                request.message,
                history,
                request.jd_context.model_dump() if request.jd_context else None,
            ):
                yield json.dumps({"token": chunk}, ensure_ascii=False) + "\n"
        except Exception as exc:
            yield json.dumps(
                {"error": str(exc), "token": ""},
                ensure_ascii=False,
            ) + "\n"

    return StreamingResponse(
        event_stream(),
        media_type="application/x-ndjson",
    )


@app.post("/api/match-job", response_model=JobMatchResponse)
def match_job(request: JobMatchRequest) -> JobMatchResponse:
    """Analyze a JD against deterministic, documented portfolio evidence."""
    if looks_like_question(request.job_description):
        raise HTTPException(
            status_code=422,
            detail={
                "code": "jd_question_input",
                "message": (
                    "This looks like a question rather than a job description. "
                    "Paste the actual JD here, or use AI Chat for questions about an existing analysis."
                ),
            },
        )
    return JobMatchResponse.model_validate(
        service.match_job(request.job_description)
    )


@app.post("/api/interview")
def interview(request: InterviewRequest) -> dict:
    """Generate the next evidence-grounded interview coaching turn."""
    raw = service.interview(
        request.focus,
        request.previous_answer,
        [message.model_dump() for message in request.history],
    )
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {
            "question": raw,
            "why_it_matters": "The local model returned an unstructured response.",
            "evaluation": "No automatic evaluation was produced.",
            "follow_up": "",
            "evidence": [],
        }
