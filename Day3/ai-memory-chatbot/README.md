# AI Memory Chatbot

A small conversational chatbot using Python, LangChain, Groq, FastAPI, and Redis.
Each `session_id` owns an independent conversation buffer. The messages are stored
in Redis, so they remain available after the Python process restarts as long as the
Redis instance keeps its data.

## Configuration

Create `.env` in the project root:

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-120b
REDIS_URL=redis://localhost:6379/0
MEMORY_TTL_SECONDS=0
```

`MEMORY_TTL_SECONDS=0` means session memory does not expire. Set a positive value
when temporary sessions are preferred.

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Redis must be running before using `/chat`. Install Redis using your operating
system package manager, or set `REDIS_URL` to a hosted Redis instance.

## Run the API

```bash
.venv/bin/uvicorn app.main:app --reload
```

The API is available at `http://127.0.0.1:8000`.

Send a message:

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"session_id":"session-a","message":"My name is Prem."}'
```

Continue the same session:

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"session_id":"session-a","message":"What is my name?"}'
```

Inspect or clear memory:

```bash
curl http://127.0.0.1:8000/memory/session-a
curl -X DELETE http://127.0.0.1:8000/memory/session-a
curl http://127.0.0.1:8000/health
```

Use a different `session_id` for another user. Memory is isolated by that ID.

## Tests

The memory tests do not need Redis or a Groq request:

```bash
.venv/bin/python -m unittest discover -s tests -v
```

## Data flow

```text
Request(session_id, message)
	↓
Redis lookup: conversation:<session_id>
	↓
Previous messages + current message
	↓
Groq via ChatGroq
	↓
Save user message and assistant response to Redis
```
