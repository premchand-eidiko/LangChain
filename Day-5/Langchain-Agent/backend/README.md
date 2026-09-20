# Backend

FastAPI service for authentication, chat persistence, document uploads, RAG, web search, LangChain agents, streaming responses, analytics, and Langfuse tracing.

## Install

From the repository root:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
Copy-Item .env.example .env
```

Add `GROQ_API_KEY` to `.env` at the repository root.

## Run

From the `backend` folder:

```powershell
..\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

The API listens on http://127.0.0.1:8000. Health check: http://127.0.0.1:8000/health

## Database

The default database is local SQLite at `data/production_ai_agent.db`. Set `DATABASE_URL` in `.env` to use PostgreSQL in deployment.

## Tests

From the repository root:

```powershell
.\.venv\Scripts\python.exe -m pytest backend\tests -q
```
