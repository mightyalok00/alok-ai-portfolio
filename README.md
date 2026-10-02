# Alok AI Portfolio

An evidence-first AI portfolio for recruiters and technical reviewers. It combines a React/Vite interface, FastAPI services, transparent portfolio retrieval, and local Ollama models.

## What this project demonstrates

- **Recruiter Mode** — compact candidate snapshot and skill evidence
- **Project Explorer** — browse documented projects and open project evidence
- **AI Recruiter Chat** — streaming, portfolio-grounded answers
- **JD Analyzer** — compare a job description with documented evidence
- **AI Interview Mode** — portfolio-grounded technical practice
- **Local AI stack** — Ollama model routing without a hosted LLM for the core workflow
- **Evidence policy** — the assistant distinguishes documented facts from missing information

## Architecture

```text
React + Vite
    │
    ├── Recruiter Mode
    ├── Project Explorer
    ├── AI Chat
    ├── JD Analyzer
    └── Interview Mode
             │
             ▼
          FastAPI
             │
       ┌─────┴────────┐
       ▼              ▼
 Portfolio Data    Retrieval
       │              │
       └──────┬───────┘
              ▼
        Model Router
              │
       ┌──────┼───────────────┐
       ▼      ▼               ▼
 llama3.2  qwen2.5-coder  deepseek-r1
              │
              ▼
            Ollama
```

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | React, Vite, React Markdown, Lucide |
| Backend | FastAPI, Pydantic |
| AI | Ollama |
| Models | llama3.2, qwen2.5-coder, deepseek-r1 |
| Retrieval | Lightweight transparent local retrieval |
| Testing | Pytest |
| Runtime | Python 3.14.7, Node.js |

## Local setup

### 1. Ollama

Make sure Ollama is running at:

```text
http://localhost:11434
```

Verify the configured models are available:

```powershell
ollama list
```

### 2. Backend

Open Terminal 1:

```powershell
cd E:\alok-ai-portfolio\backend
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

API:

```text
http://127.0.0.1:8000
http://127.0.0.1:8000/docs
```

### 3. Frontend

Open Terminal 2:

```powershell
cd E:\alok-ai-portfolio\frontend
npm install
npm run dev
```

Open the Vite URL shown in the terminal.

## API surface

- `GET /api/health`
- `GET /api/candidate`
- `GET /api/projects`
- `POST /api/chat`
- `POST /api/match-job`
- `POST /api/interview`

## Evidence policy

The portfolio assistant must not invent:

- education or CGPA
- employment history
- certifications
- achievements
- project metrics
- responsibilities
- technologies that are not documented

When evidence is missing, the application should state that it is not documented.

The exact LinkedIn profile is intentionally not included until verified.

## Repository structure

```text
alok-ai-portfolio/
├── backend/
│   ├── app/
│   ├── data/
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── public/
│   └── src/
├── docs/
├── notebooks/
├── README.md
└── .gitignore
```

## JD Analyzer pipeline

The JD Analyzer is intentionally **evidence-first and deterministic**:

1. The job description is normalized locally.
2. Documented skills and project technologies are matched against the JD.
3. Relevant projects are selected only from the verified portfolio dataset.
4. Education, certification, and employment requirements are reported as **not verified** when the corresponding candidate data is empty.
5. Ollama is not responsible for deciding whether a qualification exists, so model reasoning or malformed JSON cannot corrupt the analyzer response.
6. The API response is validated with Pydantic before it reaches the frontend.

This separation keeps the recruiter workflow grounded in `backend/data/candidate.json` and prevents local model output from inventing qualifications.
## Verification

The GitHub Actions workflow validates the backend test suite and frontend production build on pushes and pull requests to `main`.

Backend tests:

```powershell
cd backend
pytest -q
```

Frontend build:

```powershell
cd frontend
npm run build
```

## Product workflow

The recruiter workflow is designed as one evidence chain rather than independent tools:

```text
Job Description
      ↓
Requirement Match
      ↓
Relevant Projects
      ↓
Not Verified
      ↓
Traceable Evidence
      ↓
Discuss with AI
      ↓
Grounded Recruiter Chat
```

When a JD is analyzed, its deterministic result can be loaded into AI Chat as structured context. Follow-up answers must preserve the analyzer's documented-match and not-verified classifications.

## Roadmap

- GitHub repository evidence ingestion
- richer project metrics backed by source evidence
- JD-aware recruiter interview sessions
- optional recruiter resume download
- optional voice interface
- deployment with a cloud-hosted model when laptop-local Ollama is unavailable

## Links

- GitHub profile: https://github.com/mightyalok00
- Portfolio repository: https://github.com/mightyalok00/alok-ai-portfolio
