# Private AI Workspace

A local-first conversational AI application with FastAPI, React, LangChain, document RAG, web search, authentication, streaming responses, and Langfuse observability.

## Features

- JWT authentication with owner-scoped chats and documents
- Streaming Groq/LangChain responses with stop/cancel support
- Chat history with automatic first-prompt titles, rename, pin, and delete
- Chat-scoped PDF, DOCX, PPTX, TXT, and CSV uploads and retrieval
- Document cards attached to sent prompts and prompt editing
- Optional Tavily web search
- Usage analytics for users, chats, and documents in Settings
- Responsive light/dark interface with independently scrolling chat history
- Optional Langfuse tracing for model calls, tools, latency, tokens, and errors

## Requirements

- Python 3.10+ (tested with 3.13)
- Node.js 20+
- npm

## First-Time Setup

From the repository root:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and set `GROQ_API_KEY`. `SEARCH_API_KEY` is optional (Tavily web search).

Install frontend dependencies once:

```powershell
Set-Location frontend
npm ci
```

## Run Locally

Use two terminals.

**Terminal 1 — backend**

```powershell
Set-Location backend
..\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

Backend runs at http://127.0.0.1:8000

**Terminal 2 — frontend**

```powershell
Set-Location frontend
npm run dev
```

Open http://localhost:5173

SQLite is used locally at `data/production_ai_agent.db`. Tables are created automatically at startup.

### Troubleshooting

| Issue | Fix |
|---|---|
| `uvicorn` not found | Run `..\.venv\Scripts\Activate.ps1` in the `backend` folder first |
| Script execution disabled | Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once |
| `vite` not found | Run `npm ci` once in the `frontend` folder |
| AI does not respond | Add `GROQ_API_KEY` to `.env` and restart the backend |

## Environment Variables

See `.env.example` for all supported settings. Common values:

```env
GROQ_API_KEY=gsk_...
SEARCH_API_KEY=tvly-...          # optional
JWT_SECRET=change-me-in-prod
DATABASE_URL=                    # leave empty for local SQLite
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
LLM_PROVIDER=groq
LLM_MODEL=openai/gpt-oss-20b
```

## Langfuse

Tracing uses `langfuse==4.0.6` and the official LangChain callback integration:

```env
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_BASE_URL=https://cloud.langfuse.com
LANGFUSE_ENVIRONMENT=development
LANGFUSE_SAMPLE_RATE=1.0
```

Each chat turn becomes a trace grouped by chat session. Tracing is fail-open and disabled when keys are absent. Traces flush during FastAPI shutdown.

## API Highlights

```text
POST  /auth/register       POST  /auth/login
GET   /auth/me             GET   /chats
POST  /chats               PATCH /chats/{chat_id}
DELETE /chats/{chat_id}    POST  /chats/{chat_id}/message
POST  /documents/upload    GET   /documents
GET   /analytics/usage     GET   /health
```

Deleting a chat removes its messages and orphaned document files. A document shared with another chat remains available there.

## Validation

```powershell
.\.venv\Scripts\python.exe -m pytest backend\tests -q
Set-Location frontend
npm run build
```

## Repository Hygiene

Do not commit `.env`, API keys, `keys.txt`, `.venv`, `node_modules`, generated data, uploads, or build/cache folders. These are ignored by `.gitignore`.
