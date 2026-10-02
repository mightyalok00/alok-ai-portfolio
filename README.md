# Alok AI Portfolio

> **An evidence-first AI portfolio built for recruiters, technical reviewers, and hiring workflows.**

Alok AI Portfolio turns a traditional developer portfolio into an interactive recruiter workspace. It combines a **React/Vite frontend**, **FastAPI backend**, **local Ollama models**, deterministic job-description analysis, transparent portfolio retrieval, grounded recruiter chat, and JD-aware interview practice.

The central design principle is simple:

> **AI can explain documented evidence, but it must not invent qualifications.**

---

## ✨ Product Overview

The portfolio is organized around a recruiter-friendly workflow rather than a collection of disconnected pages.

| Capability | Purpose |
|---|---|
| **Recruiter Mode** | Quickly review the candidate profile, documented skills, and project evidence |
| **Project Explorer** | Explore projects and their supporting portfolio evidence |
| **AI Recruiter Chat** | Ask natural-language questions and receive portfolio-grounded answers |
| **JD Analyzer** | Deterministically compare a job description with documented candidate evidence |
| **Interview Mode** | Practice technical interview questions using the active JD and portfolio context |
| **Local AI** | Run the core AI workflow through Ollama without requiring a hosted LLM |
| **Evidence Guardrails** | Explicitly separate documented information from information that is not verified |

---

## 🎯 Why This Project Is Different

Most portfolios are static collections of links.

This project is designed as an **evidence-driven recruiter interface**:

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
Recruiter AI Chat
      ↓
JD-Aware Interview Practice
```

A job description analyzed once becomes the **active recruiter session**. That context is persisted in the browser and reused across the recruiter workflow.

This means the recruiter does not need to repeatedly paste the same JD while moving between:

- JD Analyzer
- Projects
- AI Chat
- Recruiter Mode
- Interview Mode

---

## 🧠 Evidence-First AI

The AI layer is deliberately constrained by documented portfolio evidence.

### The assistant must not invent

- Education or CGPA
- Employment history
- Certifications
- Achievements
- Project metrics
- Responsibilities
- Technologies not documented in the portfolio
- Results or experience that are not supported by evidence

When information is unavailable, the application should explicitly communicate that it is **not documented** or **not verified**.

### Deterministic JD analysis

The JD Analyzer does not delegate qualification matching to the language model.

1. The job description is normalized locally.
2. Documented skills and project technologies are matched against the JD.
3. Relevant projects are selected from the verified portfolio dataset.
4. Education, certification, and employment requirements are treated according to available candidate evidence.
5. Ollama is used for conversational assistance, not as the source of truth for qualification classification.
6. Pydantic validates the API response before it reaches the frontend.

This separation reduces hallucination risk and keeps recruiter-facing qualification claims traceable.

---

## 🏗️ Architecture

```text
┌─────────────────────────────────────────────────────┐
│                 React + Vite Frontend               │
│                                                     │
│ Recruiter Mode │ Projects │ AI Chat │ JD │ Interview│
└──────────────────────────┬──────────────────────────┘
                           │ HTTP / Streaming
                           ▼
┌─────────────────────────────────────────────────────┐
│                    FastAPI Backend                   │
│                                                     │
│ API Routes → Validation → Services → Retrieval      │
└───────────────┬──────────────────┬──────────────────┘
                │                  │
                ▼                  ▼
       ┌────────────────┐   ┌────────────────────┐
       │ Portfolio Data │   │ Transparent Local  │
       │ candidate.json │   │ Retrieval / RAG    │
       └────────────────┘   └─────────┬──────────┘
                                      │
                                      ▼
                              ┌──────────────┐
                              │ Model Router │
                              └──────┬───────┘
                                     │
                                     ▼
                                  Ollama
                                     │
                         ┌───────────┼───────────┐
                         ▼           ▼           ▼
                      llama3.2   qwen2.5-coder  deepseek-r1
```

### Key architectural principle

**Deterministic logic owns factual classification.**

**The LLM owns conversational explanation.**

This keeps the AI useful without allowing model-generated text to become the authoritative source of candidate qualifications.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React, Vite, React Markdown, Lucide |
| Backend | FastAPI, Pydantic |
| AI Runtime | Ollama |
| Models | llama3.2, qwen2.5-coder, deepseek-r1 |
| Retrieval | Lightweight transparent local retrieval |
| Testing | Pytest |
| Frontend validation | Vite production build |
| Runtime | Python 3.14.7, Node.js |

---

## 📁 Repository Structure

```text
alok-ai-portfolio/
│
├── backend/
│   ├── app/
│   │   ├── llm/
│   │   ├── rag/
│   │   ├── jd_matcher.py
│   │   ├── main.py
│   │   ├── models.py
│   │   └── services.py
│   ├── data/
│   ├── tests/
│   └── requirements.txt
│
├── frontend/
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── vite.config.*
│
├── docs/
│   ├── architecture.md
│   └── evaluation.md
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── .gitignore
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

Install:

- Python **3.14.7**
- Node.js
- npm
- Ollama
- Git

The application is designed for local development on Windows, but the architecture is portable.

---

### 1. Start Ollama

Ensure Ollama is running and verify the available models:

```powershell
ollama list
```

The default local Ollama endpoint is:

```text
http://127.0.0.1:11434
```

---

### 2. Start the FastAPI backend

Open Terminal 1:

```powershell
cd E:\alok-ai-portfolio\backend
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

---

### 3. Start the React frontend

Open Terminal 2:

```powershell
cd E:\alok-ai-portfolio\frontend
npm install
npm run dev
```

Open the Vite development URL displayed in the terminal.

---

## 🔌 API Surface

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | Backend / Ollama health information |
| GET | `/api/candidate` | Candidate profile data |
| GET | `/api/projects` | Documented portfolio projects |
| POST | `/api/chat` | Grounded recruiter conversation |
| POST | `/api/match-job` | Deterministic JD analysis |
| POST | `/api/interview` | JD-aware interview practice |

Interactive API documentation is available through FastAPI's generated Swagger UI at `/docs`.

---

## 🔍 JD Analyzer

The JD Analyzer is intentionally **deterministic and evidence-first**.

### Analysis flow

```text
Raw Job Description
        │
        ▼
Normalization
        │
        ▼
Requirement / Skill Matching
        │
        ├───────────────┐
        ▼               ▼
Matched Evidence    Not Verified
        │               │
        ▼               ▼
Relevant Projects   Explicit Gap
        │
        ▼
Structured Pydantic Response
        │
        ▼
Recruiter Workflow
```

The analyzer remains authoritative for:

- documented skill matches
- relevant projects
- requested-but-not-verified requirements
- evidence
- analysis notes

The conversational AI layer can discuss those results, but it does not replace the analyzer's classification.

---

## 💬 AI Recruiter Chat

AI Chat is designed for recruiter-style questions such as:

- “Which projects are relevant to this role?”
- “What evidence supports this skill?”
- “Which requirements are not verified?”
- “Explain this project.”
- “Give me interview questions related to this JD.”

Responses are grounded in the portfolio's documented evidence and active recruiter session.

The system favors **traceability over confident speculation**.

---

## 🎤 Interview Mode

Interview Mode uses the active recruiter session to make practice more relevant to the analyzed JD.

The interview workflow can use:

- documented portfolio skills
- relevant projects
- active JD requirements
- explicitly unverified requirements

It must not turn an unverified requirement into a claimed qualification.

---

## 🧪 Testing & CI

The repository uses automated validation rather than relying on a manually maintained validation notebook.

### Backend

```powershell
cd backend
pytest -q
```

### Frontend

```powershell
cd frontend
npm run build
```

### GitHub Actions

The CI workflow validates the backend test suite and frontend production build on pushes and pull requests targeting `main`.

This provides a reproducible baseline for changes to the application.

---

## 🔐 Data & Grounding Policy

The portfolio is designed around a strict source-of-truth boundary.

```text
Documented Portfolio Evidence
            │
            ▼
     Deterministic Logic
            │
            ▼
      Structured Context
            │
            ▼
       Local AI Model
            │
            ▼
     Grounded Explanation
```

The model should never manufacture:

- qualifications
- work history
- certifications
- project outcomes
- numerical achievements
- responsibilities
- technologies
- professional claims

The exact LinkedIn profile is intentionally not included until verified.

---

## 📊 Engineering Focus

This project demonstrates practical skills across:

- Full-stack application architecture
- React frontend development
- FastAPI backend development
- Pydantic validation
- Local LLM integration
- Ollama model routing
- Retrieval-grounded generation
- Deterministic information extraction
- Job-description analysis
- Evidence-grounded prompting
- Streaming AI responses
- Recruiter-focused UX
- Automated testing
- GitHub Actions CI
- Local-first AI application design

---

## 🗺️ Roadmap

Planned improvements include:

- GitHub repository evidence ingestion
- Richer project metrics backed by source evidence
- More detailed evidence traceability in the UI
- Optional recruiter resume download
- Optional voice interface
- Cloud model fallback when local Ollama is unavailable
- Additional automated frontend tests
- Deployment-ready production configuration

---

## 👤 Author

**Alok Agarwal**

AI / Data / Digital Technology Portfolio

- GitHub: https://github.com/mightyalok00
- Portfolio repository: https://github.com/mightyalok00/alok-ai-portfolio

---

## 📄 License

Add a repository license here if you intend to distribute the project under an open-source license.

---

<p align="center">
  <strong>Evidence first. AI second.</strong><br>
  Built to make technical portfolios easier to explore, verify, and discuss.
</p>
