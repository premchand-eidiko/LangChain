# Day 2: Prompt Templates, Models, and Chains

These folders teach the building blocks used by the final `mini-project`
project. The examples use LangChain Core and deterministic Python functions, so
they demonstrate the data flow without requiring a model API key.

## Learning order

1. `prompt-templates`: format reusable `PromptTemplate` and `ChatPromptTemplate` prompts.
2. `few-shot-templates`: guide output with examples using few-shot templates.
3. `sequential-chains`: pass the output of one runnable into the next with `RunnableSequence`.
4. `parallel-runnables`: send the same input to multiple runnables with `RunnableParallel`.
5. `dynamic-chains`: choose a runnable at runtime with `RunnableBranch`.
6. `mini-project`: final practical lab using Groq, sequential steps, and parallel tasks.

Run each practice lesson from its own folder:

```bash
python3 main.py
```

Install the dependencies used by the practice lessons from the final lab:

```bash
python3 -m pip install -r mini-project/requirements.txt
```
