# Redis Memory

Redis memory stores serialized conversation turns under a session-specific key.
Redis is useful when several processes need to share memory or when memory must
survive a process restart.

The implementation is intentionally small and mirrors the Redis part of the
final `ai-memory-chatbot` project. The tests replace the network client with a
fake client, so the lesson can run without Redis installed or running.

## Install and run

From `Day3/ai-memory-chatbot`:

```bash
python -m pip install -r requirements.txt
```

Then from this folder:

```bash
python main.py
python -m unittest -v
```

To use a real Redis server, run Redis and change the client construction in
`main.py` to `redis.Redis.from_url("redis://localhost:6379/0", decode_responses=True)`.

## Practice

Change the key prefix, add a TTL, and test two session IDs. The important rule is
that one session must never read another session's conversation.
