# PromptTemplate and ChatPromptTemplate

A prompt template is a reusable instruction with named variables. Keep the
instruction stable and provide changing values at runtime.

- `PromptTemplate` produces one text prompt.
- `ChatPromptTemplate` produces structured messages with roles such as system,
  human, and assistant.

## Run

```bash
python3 main.py
```

## Practice

Change the `topic` and `audience` values. Then add another variable to both
templates and see where it must be supplied during `invoke()`.
