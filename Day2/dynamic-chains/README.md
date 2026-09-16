# Dynamic Chains

A dynamic chain chooses its next runnable from the input. `RunnableBranch` is
useful when different request types need different prompts or processing rules.

The first matching condition is selected. The final runnable is the fallback
when no condition matches.

## Run

```bash
python3 main.py
```

## Practice

Add a `code` branch or change the fallback. Try inputs containing `summary` and
`explain` to see how the selected branch changes.
