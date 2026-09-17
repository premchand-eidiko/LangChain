# Enterprise Document Chatbot

## Project Overview

This is one beginner-friendly LangChain project that loads enterprise documents, indexes them in a local Chroma vector store, retrieves relevant chunks, and answers questions with a Groq chat model. It supports PDF files, CSV files, and public web pages.

The project has two modes:

1. **Ingestion:** load documents, split text, create embeddings, and save Chroma.
2. **Chat:** load Chroma, retrieve relevant chunks, call the LLM, and display sources.

Ingestion is done whenever documents change. Chat reuses the saved vector store for multiple questions.

## What This Demonstrates

- Document loaders and metadata
- Recursive text splitting
- Hugging Face embeddings
- Chroma vector storage and similarity search
- Configurable retrievers
- Prompt engineering and grounded RAG
- LangChain and Groq integration
- Source display in a CLI chatbot

## Architecture

```text
INGESTION
PDF / CSV / URL
    ↓
Document loader
    ↓
LangChain Documents
    ↓
RecursiveCharacterTextSplitter
    ↓
Chunks with metadata
    ↓
Hugging Face embeddings
    ↓
Persistent Chroma vector store

CHAT
User question
    ↓
Query embedding
    ↓
Similarity retriever
    ↓
Relevant Document chunks
    ↓
Prompt with context
    ↓
Groq chat model
    ↓
Answer + sources
```

The same embedding model is used for document chunks and user questions. This lets Chroma compare their vector meanings. The LLM does not search the files directly; it receives only the chunks returned by the retriever.

## Project Structure

| Path | Responsibility |
| --- | --- |
| `data/` | PDFs, CSVs, and URLs to ingest |
| `src/loaders/` | One loader per source type |
| `src/ingestion/` | Central loading pipeline and chunking |
| `src/embeddings/` | One cached Hugging Face embedding model |
| `src/vectorstore/` | Create, load, and search Chroma |
| `src/retrieval/` | Convert a vector store into a top-k retriever |
| `src/rag/` | Prompt, context formatting, and LLM workflow |
| `run.py` | Command-line entry point for `ingest`, `chat`, and `rebuild` |
| `vector_store/` | Generated local Chroma database; ignored by Git |

## Technologies

Python 3.11+, LangChain, `sentence-transformers/all-MiniLM-L6-v2`, Chroma, PyPDF, CSVLoader, BeautifulSoup/WebBaseLoader, python-dotenv, and Groq.

## Installation

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

On Windows use `.venv\Scripts\activate`. Always use the `.venv` interpreter. If `python3.11` is managed by pyenv, select it first with `pyenv local 3.11.9`.

To confirm that the terminal is using the project environment:

```bash
which python
python --version
```

The path should contain `.venv`, and the version should be Python 3.11 or newer.

## Environment Variables

Put your key in `.env`, never in source code:

```text
GROQ_API_KEY=your_key_here
GROQ_MODEL=openai/gpt-oss-20b
```

`GROQ_MODEL`, `CHUNK_SIZE`, `CHUNK_OVERLAP`, `RETRIEVAL_K`, and `EMBEDDING_MODEL_NAME` can be changed through environment variables. `.env` is ignored by Git.

## Add Documents

- Put `.pdf` files in `data/pdf/`.
- Put `.csv` files in `data/csv/`.
- Add one public URL per line to `data/web/urls.txt`.

The loaders preserve source metadata, and PDF page metadata is shown in answers when available.

## Build the Vector Store

```bash
python run.py ingest
```

The command performs this sequence:

```text
Files and URLs
    -> loader
    -> Documents
    -> chunks
    -> embeddings
    -> vector_store/
```

It prints document and chunk counts. One multi-page PDF can produce multiple Documents. Running ingestion again rebuilds the local vector store so changed documents do not create duplicate chunks.

## Start the Chatbot

```bash
python run.py chat
```

Chat mode loads the existing `vector_store/`, creates a top-k similarity retriever, and starts the Groq model. It does not rebuild embeddings for every question.

Example questions depend on your documents:

- `What is the leave policy?`
- `Which department owns the onboarding process?`
- `What does the document say about working hours?`

Each response includes retrieved sources when metadata is available. Type `exit` to end the session. `python run.py rebuild` is an alias for ingestion.

## Component Responsibilities

| Component | Responsibility |
| --- | --- |
| Document Loader | Converts a source into LangChain `Document` objects |
| Text Splitter | Makes searchable chunks and preserves metadata |
| Embedding Model | Converts text and questions into numeric vectors |
| Vector Store | Persists vectors and performs similarity search |
| Retriever | Exposes a configurable document retrieval interface |
| Prompt | Tells the LLM how to use context and avoid invention |
| LLM | Generates the final natural-language answer |
| RAG Chain | Connects retrieval, context formatting, prompting, and generation |

## How to Explain the Project

The shortest accurate explanation is:

> During ingestion, loaders convert PDFs, CSVs, and web pages into LangChain Documents. The splitter creates smaller chunks while preserving metadata. Hugging Face converts the chunks into vectors, and Chroma stores those vectors locally. During chat, the user's question is embedded and the retriever finds similar chunks. Those chunks are placed into a grounded prompt, Groq generates the answer, and the application displays the sources.

The main code path is:

```text
run.py
    -> src.main.ingest() or src.main.chat()
    -> loaders / splitter / vector store
    -> retriever
    -> src.rag.rag_chain.answer_question()
    -> answer + sources
```

For a deeper explanation, trace the files in the project structure from `run.py` to `src/main.py`, then into the loader, ingestion, vector store, retrieval, and RAG modules.

## Troubleshooting

- `GROQ_API_KEY is missing`: copy `.env.example` to `.env` and add a valid key.
- `Vector store not found`: run `python run.py ingest` first.
- `No documents found`: add supported files or URLs to `data/`.
- Web loading fails: check that the URL is public and reachable.
- Embedding download fails: check network access and rerun ingestion.
- A model error occurs: set `GROQ_MODEL` in `.env` to a model available to your Groq account.
- SQLite or Chroma compatibility error: reinstall the dependencies from `requirements.txt`; the project includes `pysqlite3-binary` for older system SQLite versions.

## Future Improvements

Possible next steps include incremental ingestion, richer metadata filters, a web UI, authentication, and evaluation datasets. They are intentionally outside this focused learning project.
