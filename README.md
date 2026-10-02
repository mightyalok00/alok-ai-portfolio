# Alok AI Portfolio — Ollama Edition v3

A recruiter-facing AI portfolio combining a modern React portfolio, FastAPI,
local Ollama model routing, evidence retrieval, JD analysis, and interview coaching.

## What is new in v3

- Professional portfolio homepage instead of a chatbot-only screen
- Project Explorer
- Recruiter AI Chat
- Job Description Analyzer
- Portfolio Interview Mode
- Local model routing
- Evidence-grounded prompting
- Lightweight transparent local retrieval
- Source links to GitHub/live demos
- Evaluation test suite
- React/Vite runtime fix
- Python 3.14.7 target
- No cloud LLM required for the core workflow

## Local stack

```text
React + Vite
      |
      v
FastAPI
  |       \
  |        +--> JD Analyzer
  |
  +--> Retrieval --> Portfolio Evidence
  |
  +--> Model Router
          |
          +--> llama3.2:latest
          +--> qwen2.5-coder:7b
          +--> deepseek-r1:7b
                    |
                    v
               Ollama
                    |
                    v
              RTX 3050 6GB
```

## Your confirmed Ollama setup

- Ollama 0.35.0
- `http://localhost:11434`
- `llama3.2:latest`
- `qwen2.5-coder:7b`
- `deepseek-r1:7b`
- NVIDIA RTX 3050 6 GB
- 24 GB RAM
- Python 3.14.7

## Run

### Backend

```powershell
cd E:\alok-ai-portfolio-ollama-v3\backend
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

### Frontend

Open another terminal:

```powershell
cd E:\alok-ai-portfolio-ollama-v3\frontend
npm install
npm run dev
```

Open the URL shown by Vite, normally:

```text
http://localhost:5173/
```

## Features

### AI Chat

Ask about documented projects, skills, technologies, and portfolio evidence.
Responses stream from Ollama.

### Project Explorer

Browse project cards with technologies and source links.

### JD Analyzer

Paste a job description. The application returns:

- documented skill matches
- relevant projects
- evidence
- requested but not verified requirements
- notes

It does not produce a hiring verdict.

### Interview Mode

Choose a focus such as Python, SQL, ML, GenAI, or FastAPI. The local reasoning
model generates a portfolio-grounded interview question and can coach a supplied answer.

## Evidence policy

The AI must not fabricate:

- CGPA
- education
- employment
- certifications
- achievements
- project metrics
- responsibilities
- technologies not supported by evidence

When information is missing, it should say that it is not documented.

LinkedIn is intentionally left empty until the exact profile is verified.

## RAG roadmap

The current retrieval layer is transparent and dependency-light. It can later be
replaced with:

```text
Sentence Transformers
        ↓
Embeddings
        ↓
Qdrant / Chroma
        ↓
Semantic retrieval
        ↓
Ollama
```

The service interface is already separated to make that migration straightforward.

## Evaluation

See `docs/evaluation.md`.

Run:

```powershell
cd backend
pytest -q
```

The tests cover:

- candidate validation
- API health
- project endpoint
- routing
- retrieval
- evidence policy

## Important data note

The profile intentionally leaves unverified personal/professional fields empty.
Repository names are not treated as proof of employment, education, certification,
or performance metrics.

The project currently contains documented GitHub portfolio information supplied
during development. A future GitHub ingestion step should fetch the actual README
and source evidence for every repository before deployment.
