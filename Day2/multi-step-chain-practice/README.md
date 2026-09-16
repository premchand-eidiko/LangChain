# Building Multi-Step Chains

This practice note connects the earlier lessons into one design:

1. A prompt template prepares the input.
2. A model or deterministic function produces an answer.
3. A formatter cleans the result.
4. A parallel group creates independent learning materials.
5. The final dictionary combines the outputs.

The complete API-backed implementation is in `../mini-project`. Read its
`main.py` after practicing the smaller lessons to see how the pieces fit
together with `ChatGroq`.

## Existing practical lab

```bash
cd ../mini-project
python3 main.py
```

That lab needs the dependencies in `requirements.txt`, a `.env` file containing
`GROQ_API_KEY`, and internet access.
