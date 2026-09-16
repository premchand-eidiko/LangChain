# Summary Memory

Summary memory keeps recent turns and compresses older turns into a short text
summary. This controls prompt size, but compression can lose details.

This lesson uses a deterministic summarizer so it works without an API key. In a
real chatbot, replace `summarize()` with an LLM call and keep the same memory
boundary.

## Run and test

```bash
python main.py
python -m unittest -v
```

## Practice

Change `max_recent_turns` to `4` and observe when the summary starts changing.
Compare the full buffer with the compact context returned by `load_context()`.
