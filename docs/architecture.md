# Architecture

React/Vite sends recruiter questions to FastAPI. FastAPI retrieves matching Markdown evidence, routes the question to an installed Ollama model, and streams the result back as NDJSON.

Model roles:
- General: llama3.2:latest
- Technical/code: qwen2.5-coder:7b
- JD/reasoning: deepseek-r1:7b

The 6 GB RTX 3050 means the application should avoid concurrent heavyweight generations. Lightweight keyword retrieval is intentionally used first; embeddings and a vector DB can replace it later.
