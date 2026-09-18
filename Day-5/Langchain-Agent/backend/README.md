# Backend

The FastAPI backend will own authentication, chat persistence, document processing, retrieval, tools, and agent orchestration.

## Current Backend

The backend includes authentication, owner-scoped chats and documents, upload-time indexing, RAG retrieval, web search, conversation context, and the streaming agent endpoint. It defaults to SQLite for local development and initializes tables at startup. Set `DATABASE_URL` to PostgreSQL for deployment.

Important endpoints:

```text
POST /auth/register
POST /auth/login
GET  /auth/me
GET  /chats
POST /chats
POST /chats/{chat_id}/message
POST /documents/upload
GET  /documents
```

Database tables can be initialized after PostgreSQL is running:

```bash
PYTHONPATH=backend python -m app.database.init_db
```

Authentication, chat APIs, and AI features are intentionally added in later phases.

Run from the repository root after installing `backend/requirements.txt`:

```bash
uvicorn backend.app.main:app --reload
```
