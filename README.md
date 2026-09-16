# LangChain Learning Workspace

This workspace contains independent learning days and mini-projects.

## Environments

There are two environment levels:

- **Common learning environment:** the root `.venv` is for the Day 1, Day 2,
  and Day 3 practice lessons. Its dependencies are in the root
  `requirements.txt`.
- **Mini-project environments:** `Day1/chain-app`, `Day2/mini-project`, and
  `Day3/ai-memory-chatbot` keep their own `requirements.txt`, `.venv`, and
  configuration. Do not replace those environments with the root environment.

## Create the common environment

From this folder:

```bash
python3.9 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If `python3.9` is unavailable, use another Python 3 version supported by the
installed package versions.

Verify it:

```bash
.venv/bin/python -c "import langchain, langchain_core; print(langchain.__version__)"
```

## Shared configuration

Copy `.env.example` to `.env` and add only the keys needed by the exercise:

```bash
cp .env.example .env
```

The root `.env` is ignored by Git. The mini-projects may have their own `.env`
files with project-specific settings; those files remain independent.

## Run learning lessons

Activate the common environment from the workspace root:

```bash
source .venv/bin/activate
python Day2/prompt-templates/main.py
python Day2/multi-step-chain-practice/main.py
python Day3/buffer-memory/main.py
```

## Run a mini-project independently

Use the README and environment inside that project. For example:

```bash
cd Day3/ai-memory-chatbot
source .venv/bin/activate
python -m pip install -r requirements.txt
```

The root setup does not modify or replace any mini-project environment.
