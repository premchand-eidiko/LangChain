# Day 3: Memory Systems

This directory contains the Day 3 learning path for conversational AI memory.
The folders before `ai-memory-chatbot` are small, focused practice projects. The
final project combines conversation memory with a Groq-powered API and Redis.

## Learning order

1. `buffer-memory`: keep the complete conversation in memory.
2. `summary-memory`: replace old turns with a compact summary.
3. `entity-memory`: keep structured facts about people, projects, and preferences.
4. `longterm-memory`: persist facts in a JSON file across program restarts.
5. `redis-memory`: store session conversations in Redis with a fake client test.
6. `ai-memory-chatbot`: use Redis memory in a FastAPI chatbot.

The practice folders use the shared environment at the workspace root. From a
practice folder, activate it with:

```bash
source ../../../.venv/bin/activate
python main.py
```

For example, from `Day3/buffer-memory`, the command is exactly
`source ../../../.venv/bin/activate`. The final `ai-memory-chatbot` project has
its own environment and setup instructions; do not replace it with the shared
environment.
