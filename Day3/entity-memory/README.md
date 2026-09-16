# Entity Memory

Entity memory stores facts grouped by entity instead of storing only a raw
conversation. It is useful when a chatbot needs to remember that a person likes
Python or that a project uses Redis.

This example uses explicit `remember()` calls. Production applications often use
an LLM or a validated extractor to turn messages into these structured facts.

## Run and test

```bash
python main.py
python -m unittest -v
```

## Practice

Add a new entity such as `project` and retrieve it with `get()`. Notice that
entity memory is structured and easy to inspect, unlike a plain transcript.
