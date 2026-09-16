# Long-Term Memory

Long-term memory persists useful facts beyond one Python process. This lesson
uses a JSON file to make the storage easy to inspect. A database or vector store
can replace the file later without changing the idea: load facts, update them,
and save them.

## Run and test

```bash
python main.py
python -m unittest -v
```

The demo writes `memory.json` in the folder. It is ignored by the test suite and
can be deleted when you want a fresh start.

## Practice

Stop and run `python main.py` again. The second run loads the fact saved by the
first run, which demonstrates the difference between in-process memory and
persistent memory.
