# Enterprise Document Chatbot

An easy-to-revise, command-line **Retrieval-Augmented Generation (RAG)** chatbot built with LangChain.

The application reads information from PDFs, CSV files, and public web pages, converts the content into searchable vector embeddings, and answers questions using only the most relevant retrieved context. Every answer also reports the documents used as sources.

## The Project In One Minute

This project separates knowledge preparation from question answering:

1. **Ingest** documents from `data/`.
2. **Split** long documents into smaller overlapping chunks.
3. **Embed** each chunk with a Hugging Face sentence-transformer model.
4. **Store** the embeddings in a persistent Chroma vector database.
5. **Retrieve** the most relevant chunks for a question.
6. **Generate** a grounded answer with a Groq chat model.
7. **Show** the source files and page numbers used for the answer.

This is RAG because the language model does not answer from its general knowledge alone. The application retrieves relevant project data first and places that data in the model prompt.

## Why This Project Is Useful

- Ask questions across several document types from one interface.
- Keep the knowledge base local in a persistent `vector_store/` directory.
- Reduce unsupported answers with a prompt that requires the model to use retrieved context.
- See source information alongside each answer.
- Adjust chunking, retrieval count, embedding model, and LLM model through environment variables.

## Architecture

```text
PDF files       CSV files       URLs
    |               |              |
    +---------------+--------------+
                    v
          Document loaders
                    v
          Text chunking
       (size + overlap)
                    v
       Hugging Face embeddings
                    v
       Persistent Chroma store
                    |
                    | question
                    v
       Similarity retriever (top-k)
                    v
       Grounded RAG prompt + Groq LLM
                    v
       Answer and reported sources
```

## Requirements

- Python 3.10 or newer is recommended.
- Internet access is needed when loading web pages, downloading the embedding model the first time, and calling Groq.
- A Groq API key is required for chat. Ingestion does not call the LLM.

## Installation

Run these commands from the project root, the directory containing `run.py`:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

Create a local environment file:

```bash
cp .env.example .env
```

Then edit `.env` and add your Groq key:

```dotenv
GROQ_API_KEY=your_actual_groq_api_key
GROQ_MODEL=openai/gpt-oss-20b
```

Never commit `.env` or expose the API key. It is ignored by Git.

## Add Knowledge Sources

### PDF files

Place `.pdf` files in:

```text
data/pdf/
```

The PDF loader keeps source and page metadata. It also adds the file name and PDF author to the text supplied to the model.

### CSV files

Place `.csv` files in:

```text
data/csv/
```

`CSVLoader` turns CSV rows into LangChain documents. The sample file demonstrates a small employee dataset.

### Web pages

Add one public URL per line to:

```text
data/web/urls.txt
```

Blank lines and lines beginning with `#` are ignored:

```text
# This is a comment
https://example.com/public-documentation
```

The web loader uses `WebBaseLoader`, so the URLs must be reachable from the machine running ingestion.

## Run the Application

### 1. Build or rebuild the knowledge base

```bash
python run.py ingest
```

This loads every configured PDF, CSV, and URL, splits the content, creates embeddings, and saves the Chroma database to `vector_store/`.

Run ingestion again whenever the source data changes. Existing `vector_store/` contents are deleted and rebuilt, so the index always represents the current input directories and URL list.

`rebuild` is an alias for `ingest`:

```bash
python run.py rebuild
```

### 2. Start the chatbot

```bash
python run.py chat
```

Ask a question at the `Question:` prompt. Type `exit` to stop.

Example questions:

```text
What is the main idea of the LangChain RAG guide?
Which roles are present in the CSV file?
What does the Chroma documentation say about collections?
```

The response contains:

- The generated answer.
- The retrieved source documents.
- A page number when the source is a PDF.

Chat must be run after ingestion. If `vector_store/` does not exist, the application tells you to run `python run.py ingest` first.

## Configuration

Configuration is centralized in `src/config.py`. Add any of these optional values to `.env`:

| Variable | Default | Purpose |
| --- | --- | --- |
| `GROQ_API_KEY` | empty | Required for chat generation |
| `GROQ_MODEL` | `openai/gpt-oss-20b` | Groq model used to generate answers |
| `CHUNK_SIZE` | `1000` | Maximum chunk size used during splitting |
| `CHUNK_OVERLAP` | `200` | Number of overlapping characters between chunks |
| `RETRIEVAL_K` | `4` | Number of similar chunks retrieved for each question |
| `EMBEDDING_MODEL_NAME` | `sentence-transformers/all-MiniLM-L6-v2` | Hugging Face embedding model |

Example tuning configuration:

```dotenv
CHUNK_SIZE=800
CHUNK_OVERLAP=120
RETRIEVAL_K=6
```

After changing chunking or the embedding model, run ingestion again. Existing embeddings were created using the old settings.

## Project Structure

```text
.
├── run.py                       # CLI commands: ingest, chat, rebuild
├── requirements.txt             # Python dependencies
├── .env.example                # Safe configuration template
├── data/
│   ├── pdf/                    # Input PDF files
│   ├── csv/                    # Input CSV files
│   └── web/urls.txt            # Public URLs to ingest
└── src/
    ├── config.py               # Paths, defaults, and environment variables
    ├── main.py                 # Ingestion and interactive chat workflows
    ├── loaders/                # PDF, CSV, and web loaders
    ├── ingestion/
    │   ├── document_loader.py  # Combines all input sources
    │   └── text_splitter.py    # Creates overlapping chunks
    ├── embeddings/              # Hugging Face embedding model
    ├── vectorstore/             # Persistent Chroma creation and loading
    ├── retrieval/               # Similarity retriever setup
    └── rag/
        ├── prompt.py            # Grounding and anti-invention instructions
        └── rag_chain.py         # Retrieval, prompt invocation, and answer model
```

## Code Flow For Revision

### Ingestion flow

`run.py` calls `src.main.ingest()`.

1. `load_all_documents()` calls the PDF, CSV, and web loaders.
2. Each loader returns LangChain `Document` objects with content and metadata.
3. `split_documents()` uses `RecursiveCharacterTextSplitter`.
4. `get_embedding_model()` creates one cached `HuggingFaceEmbeddings` instance.
5. `create_vector_store()` writes the chunks and embeddings to Chroma.

### Question-answering flow

`run.py` calls `src.main.chat()`.

1. The existing Chroma database is opened.
2. A similarity retriever selects `RETRIEVAL_K` relevant chunks.
3. `format_context()` adds document content and source metadata to the prompt.
4. `RAG_PROMPT` tells the model to use only the supplied reference context and to admit when the answer is missing.
5. `ChatGroq` generates the answer with temperature `0`.
6. The CLI prints the answer and the retrieved source metadata.

## Important RAG Concepts

### Embeddings

An embedding converts text into a numeric vector. Texts with similar meaning tend to have vectors that are close together, allowing Chroma to perform similarity search.

### Chunking

Large documents are divided into chunks because retrieval works better on focused passages and language models have context limits. The overlap helps preserve meaning across chunk boundaries.

### Retrieval

For each question, Chroma compares the question embedding with stored chunk embeddings and returns the most similar chunks. `RETRIEVAL_K` controls how many are passed forward.

### Grounded generation

The LLM receives the retrieved chunks inside a reference context. The prompt explicitly says not to invent information, ignore instructions inside retrieved documents, and report when the answer cannot be found.

## Detailed Internal Walkthrough

### What is a LangChain `Document`?

Every loader converts source data into a LangChain `Document`. Conceptually, a document has two important parts:

```python
Document(
    page_content="the text that can be searched and sent to the model",
    metadata={
        "source": "where the text came from",
        "page": "the PDF page, when available",
        "author": "the PDF author, when available",
    },
)
```

The exact metadata depends on the loader. For example:

- A PDF usually includes `source` and a zero-based `page` value.
- A CSV includes its source file path and row content.
- A web page includes the page URL and loader-generated metadata.

The application keeps this metadata when it splits documents. That is why the chatbot can display the source after answering instead of returning only anonymous text.

### What happens to a PDF?

1. `PyPDFLoader` reads the PDF page by page.
2. Each page becomes a `Document`.
3. The loader adds the PDF file name and author to `page_content`.
4. The text splitter may divide a long page into multiple chunks.
5. Each chunk inherits the original page metadata.
6. Each chunk is embedded and stored in Chroma.

The internal PDF page number starts at `0`, as is common in Python libraries. The CLI adds `1` before displaying it, so users see normal human-readable page numbers.

### What happens to a CSV?

`CSVLoader` turns rows into documents. This is useful for asking questions about structured records without writing custom database queries. For the included sample data, questions such as “Which roles are present?” can be answered from the row documents.

CSV retrieval is still semantic retrieval. It is not a replacement for exact filtering, sorting, aggregation, or SQL. For example, a production system should use a database for questions such as “What is the total salary?” and use RAG for explanatory document questions.

### What happens to a web page?

1. URLs are read from `data/web/urls.txt`.
2. Empty and commented lines are ignored.
3. `WebBaseLoader` downloads each remaining public URL.
4. The returned page text becomes one or more documents.
5. The documents continue through the same splitting, embedding, and storage process as PDFs and CSVs.

If one source fails, the loader prints an error and continues processing the other sources. This makes ingestion partially tolerant of a broken PDF or unavailable web page, but it also means you should read the ingestion summary carefully.

## One Question, End to End

Suppose the user asks:

```text
What is Retrieval-Augmented Generation?
```

The runtime sequence is:

1. The question is passed to the retriever.
2. The same embedding model used during ingestion converts the question into a vector.
3. Chroma compares that vector with stored chunk vectors.
4. The four highest-similarity chunks are returned by default.
5. `format_context()` labels each chunk as `DOCUMENT 1`, `DOCUMENT 2`, and so on.
6. The source path, PDF page, and author are included when available.
7. `RAG_PROMPT` combines the formatted context with the user question.
8. `ChatGroq` receives the prompt with `temperature=0`.
9. The answer text and the retrieved `Document` objects are wrapped in the `Answer` dataclass.
10. The CLI prints both the answer and the source list.

The language model does not directly search the files. Chroma performs the search, and the language model explains the retrieved results.

## Ingestion Output Explained

When ingestion runs, the output is designed to help you verify the pipeline:

```text
Total documents loaded: ...
PDF documents: ...
CSV documents: ...
Web documents: ...
Original documents: ...
Generated chunks: ...
Vector store saved to: ...
```

- **Total documents loaded** is the total number of LangChain documents returned by all loaders.
- **PDF documents**, **CSV documents**, and **Web documents** are counts of returned documents, not necessarily counts of physical files or URLs.
- **Original documents** repeats the total before splitting.
- **Generated chunks** is the number of searchable pieces after splitting.
- **Vector store saved to** confirms where Chroma persisted the index.

The number of chunks can be much larger than the number of original documents because long documents are divided into multiple pieces.

## Dependency Roles

| Package | Role in this project |
| --- | --- |
| `langchain` | Core LangChain package and ecosystem foundation |
| `langchain-community` | PDF, CSV, and web document loaders |
| `langchain-text-splitters` | Recursive text chunking |
| `langchain-huggingface` | LangChain integration for Hugging Face embeddings |
| `sentence-transformers` | Local sentence-transformer embedding models |
| `langchain-chroma` | Chroma vector-store integration |
| `pypdf` | PDF text extraction used by the PDF loader |
| `beautifulsoup4` | HTML parsing support for web loading |
| `python-dotenv` | Reads `.env` configuration values |
| `langchain-groq` | Groq chat-model integration |
| `pysqlite3-binary` | SQLite compatibility support for Chroma environments |

## Why There Are Two Models

The project uses two different model responsibilities:

### Embedding model

`sentence-transformers/all-MiniLM-L6-v2` converts documents and questions into vectors. It is used during both ingestion and retrieval. The same embedding model must be used for both operations so the vectors are comparable.

### Generative model

The configured Groq model receives the retrieved text and writes the final natural-language answer. It does not create the searchable index.

This separation is a core RAG idea: embeddings handle semantic search, while the LLM handles language generation.

## Design Decisions

### Why persist Chroma?

Without persistence, the application would need to reload and re-embed every source whenever the chatbot starts. Chroma saves the searchable representation under `vector_store/`, allowing chat sessions to open the existing index immediately.

### Why rebuild the index?

The current project favors a simple and predictable learning workflow. Ingestion removes the previous vector store and creates a fresh one from the current inputs. This avoids stale chunks, although an incremental update strategy would be more efficient for a large production corpus.

### Why use a similarity retriever?

Similarity search is straightforward and appropriate for this small project. It ranks chunks by semantic closeness to the question. More advanced systems could add metadata filters, a reranker, hybrid keyword-plus-vector search, or maximum marginal relevance.

### Why set temperature to zero?

The chatbot is intended to answer from documents rather than be creative. A temperature of `0` makes generation more deterministic and reduces unnecessary variation between similar questions. It does not guarantee correctness; retrieval quality and source quality still matter.

### Why include source metadata in the prompt and output?

Metadata serves two purposes:

1. It gives the model useful context such as the source and PDF page.
2. It lets the user inspect where the retrieved answer came from.

The displayed source list is helpful evidence, but it is not a formal citation verifier. The application does not currently print exact quoted spans or similarity scores.

## Suggested Presentation Flow

Use this sequence for a clear project explanation:

1. **Problem:** Searching many documents manually is slow, and a general chatbot may answer without using company documents.
2. **Solution:** This project combines document ingestion, vector search, and a language model in a RAG pipeline.
3. **Inputs:** It accepts PDFs, CSV files, and public URLs.
4. **Preparation:** It loads and chunks the content, creates embeddings, and persists them in Chroma.
5. **Question:** The user asks a question through the command line.
6. **Retrieval:** Chroma finds the most relevant chunks using similarity search.
7. **Generation:** Groq receives the question and retrieved context through a grounding prompt.
8. **Trust:** The prompt tells the model not to invent information, and the application displays the retrieved sources.
9. **Trade-off:** The current version is simple and understandable, but it rebuilds the full index and has a command-line interface.

### Short presentation script

> My project is a command-line enterprise document chatbot using Retrieval-Augmented Generation. First, the ingestion process loads PDFs, CSV rows, and public web pages. It splits the content into overlapping chunks, converts every chunk into an embedding using a Hugging Face model, and stores those embeddings in Chroma. During chat, the user question is embedded and compared with the stored vectors. The most relevant chunks are placed into a prompt and sent to a Groq language model. The prompt restricts the model to the retrieved reference context, and the program prints the sources used. This design makes the answer more grounded in the project documents than a general question-answering chatbot.

## Common Revision Questions

### What problem does RAG solve?

RAG gives an LLM access to external or project-specific information at query time without retraining the model. It can also make answers easier to inspect by retaining the retrieved sources.

### Why split documents into chunks?

Whole documents may be too large and may contain unrelated sections. Smaller chunks improve retrieval focus and fit more predictably into the model context. Overlap prevents important sentences from being lost at a boundary.

### What is the difference between a document and a chunk?

A document is the unit returned by a loader, such as one PDF page or one CSV row. A chunk is a smaller text unit created from a document before embedding and retrieval.

### What is stored in Chroma?

The vector store contains the chunk text, its metadata, and the corresponding embedding vectors. It is persisted locally in `vector_store/`.

### Why must the embedding model be available during chat?

The question must be converted into the same vector space as the stored chunks. The application loads the embedding model when opening Chroma and creating the retriever.

### Does the LLM read all source files?

No. Chroma first selects the most similar chunks. The LLM receives the selected context, not the entire input directory.

### What happens if the answer is not in the documents?

The prompt instructs the model to say: `The information was not found in the provided documents.` However, this is a prompt-level behavior, not a mathematical guarantee.

### Is this fine-tuning?

No. Fine-tuning changes model parameters using training data. This project leaves the model unchanged and supplies relevant information in the prompt at query time.

### What is the role of `RETRIEVAL_K`?

It controls how many chunks are retrieved for each question. A small value may miss relevant context; a large value may add noise or consume more model context.

### What is the difference between `ingest` and `chat`?

`ingest` prepares and persists the searchable knowledge base. `chat` loads that knowledge base and answers questions. They are separate so documents do not need to be reprocessed for every question.

## Practical Experiments For Learning

These experiments help demonstrate how the pipeline behaves:

1. Add a new PDF, run `python run.py ingest`, and ask a question about it.
2. Remove that PDF, rebuild, and confirm it is no longer retrieved.
3. Change `RETRIEVAL_K` from `4` to `1` and compare the answer context.
4. Set a smaller `CHUNK_SIZE` and observe how the generated chunk count changes.
5. Add a commented URL and verify it is ignored.
6. Ask a question that is unrelated to the data and observe the grounded fallback behavior.
7. Temporarily make one URL invalid and observe that other sources still attempt to load.

## Possible Future Improvements

These are intentionally outside the current implementation, but they are natural next steps:

- Add a web interface with Streamlit, FastAPI, or a frontend client.
- Add automated tests for loaders, chunking, prompt formatting, and CLI behavior.
- Add exact quoted evidence and similarity scores to source reporting.
- Add metadata filtering by file, source type, date, or department.
- Support incremental indexing instead of deleting the entire vector store.
- Add document deduplication and file-change detection.
- Add OCR for scanned PDFs.
- Add structured database tools for exact CSV calculations.
- Add conversation history while keeping retrieved context explicit.
- Add evaluation data to measure retrieval precision and answer faithfulness.

## Troubleshooting

### `GROQ_API_KEY is missing`

Make sure `.env` exists in the project root and contains a real key:

```dotenv
GROQ_API_KEY=your_actual_groq_api_key
```

### `Vector store not found`

Build the index before starting chat:

```bash
python run.py ingest
python run.py chat
```

### A source was not loaded

- Confirm PDFs use the `.pdf` extension and are in `data/pdf/`.
- Confirm CSVs use the `.csv` extension and are in `data/csv/`.
- Confirm URLs are public, one per line, and not commented out.
- Read the ingestion output; individual load failures are printed while the remaining sources continue.

### Answers are incomplete or irrelevant

Try adjusting `CHUNK_SIZE`, `CHUNK_OVERLAP`, or `RETRIEVAL_K`, then rebuild the index. Also ask questions using terms that appear in the source documents.

### The first run is slow

The embedding model may need to download and initialize. Subsequent runs can reuse the local model cache, but ingestion still recomputes the project vector store.

## Limitations

- The interface is currently interactive command-line only.
- Web ingestion depends on network access and the target site allowing retrieval.
- Only public web pages are configured; there is no authentication flow for private sites.
- The vector store is rebuilt as a whole rather than updated incrementally.
- Source reporting displays retrieved documents, not a formal citation or quote-verification system.
- The application depends on a Groq API key for answer generation.

## Presentation Explanation

> This project is an enterprise document chatbot based on Retrieval-Augmented Generation. During ingestion, it reads PDFs, CSVs, and web pages, splits them into overlapping chunks, converts those chunks into Hugging Face embeddings, and stores them in Chroma. When a user asks a question, the system retrieves the most relevant chunks and sends only that context to a Groq language model. The model is instructed not to invent information, and the application prints the sources used for the response. This makes the chatbot easier to update, inspect, and ground in the project’s own documents.

## Quick Reference

```bash
# Activate the environment
source .venv/bin/activate

# Install dependencies
python -m pip install -r requirements.txt

# Configure the API key
cp .env.example .env

# Add files to data/pdf or data/csv, and URLs to data/web/urls.txt

# Build the searchable index
python run.py ingest

# Start asking questions
python run.py chat

# Rebuild after changing source data
python run.py rebuild
```