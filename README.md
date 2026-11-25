# Idea-to-Post

Turns a rough idea into a ready-to-publish social media post using a local LLM.

## Prerequisites
- Docker + Docker Compose
- [Ollama](https://ollama.com) installed on the host machine
- Model pulled: `ollama pull qwen3:1.7b`

## Run

```bash
# 1. Start Ollama on host
ollama serve

# 2. In another terminal, from this repo root:
docker compose up --build
```

- Frontend: http://localhost:3000
- API docs:  http://localhost:8000/docs

## Architecture
- **Frontend**: Next.js 14 (App Router) + Tailwind
- **Backend**:  FastAPI + SQLAlchemy (async) + aiomysql
- **LLM**:      Ollama running on host, model `qwen3:1.7b`
- **DB**:       MySQL 8

## Notes
- The 1.7B model is fast but quality is best-effort. The prompt enforces a
  JSON schema and the backend retries once on parse failure.
- Scheduling/analytics are intentionally out of scope for v0.