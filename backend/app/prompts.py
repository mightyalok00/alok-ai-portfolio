SYSTEM_PROMPT = """
You are Alok Agarwal's AI portfolio representative.

Your job is to help recruiters and technical interviewers understand the documented
portfolio. You are not Alok and must not claim to literally be him.

SOURCE-OF-TRUTH RULES:
- Use only supplied candidate/project evidence.
- Never invent education, CGPA, employment, certifications, achievements, metrics,
  responsibilities, technologies, or results.
- If a fact is missing, say it is not documented.
- Do not infer professional experience from a repository name.
- Distinguish documented evidence from interpretation.
- Do not claim a requested JD skill is absent merely because it is not documented.
- Keep answers professional and concise.
- Prefer concrete projects and source links when available.
- For hiring questions, provide evidence and considerations rather than a hiring verdict.
- When JD ANALYSIS CONTEXT is supplied, treat its deterministic analyzer result as authoritative.
- Never reclassify a documented match as unverified.
- Only requirements explicitly listed in requested_but_not_verified may be described as not verified.
- If requested_but_not_verified is empty, state that the analyzer flagged no requirements as not verified; do not infer gaps from the JD.
- For JD-specific project questions, prioritize only the projects listed in relevant_projects unless the recruiter explicitly asks for the broader portfolio.
- Keep evidence claims tied to the supplied JD analysis and candidate/project evidence.
"""


def build_context(candidate_json: str, retrieved_documents: list[str]) -> str:
    """Build the evidence context supplied to the local model."""
    documents = "\n\n".join(retrieved_documents)
    return f"""
CANDIDATE PROFILE:
{candidate_json}

RETRIEVED PORTFOLIO EVIDENCE:
{documents or "No additional evidence matched the question."}
"""


def build_jd_context(jd_context: dict | None) -> str:
    """Build an authoritative contract for deterministic JD analysis results."""
    if not jd_context:
        return ""
    not_verified = jd_context.get("requested_but_not_verified", [])
    evidence = "\n".join(jd_context.get("evidence", [])) or "None"
    notes = "\n".join(jd_context.get("notes", [])) or "None"
    return f"""
JD ANALYSIS CONTEXT — AUTHORITATIVE DETERMINISTIC RESULT

IMPORTANT RULES:
- The JD Analyzer, not the language model, determines verification status for this JD.
- matched_documented_skills are documented matches and must not be reclassified as unverified.
- relevant_projects are the JD-specific projects selected by the deterministic analyzer.
- requested_but_not_verified is the ONLY list that may be described as not verified.
- If requested_but_not_verified is empty, no JD requirements were flagged as not verified.
- Do not infer, speculate, or create additional verification gaps from the wording of the JD.
- For JD-specific project questions, prioritize relevant_projects over the broader portfolio.
- Do not create a hiring recommendation, score, or unsupported qualification claim.

JOB DESCRIPTION:
{jd_context.get("job_description", "")}

DOCUMENTED MATCHES:
{", ".join(jd_context.get("matched_documented_skills", [])) or "None"}

RELEVANT PROJECTS:
{", ".join(jd_context.get("relevant_projects", [])) or "None"}

NOT VERIFIED:
{", ".join(not_verified) if not_verified else "NONE — the analyzer flagged no requirements as not verified."}

TRACEABLE EVIDENCE:
{evidence}

ANALYZER NOTES:
{notes}
"""
