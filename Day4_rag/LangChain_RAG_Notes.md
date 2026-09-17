# 🧠 LangChain RAG — Complete Notes

> **Retrieval-Augmented Generation (RAG) with LangChain**
>
> A beginner-friendly, GitHub-ready reference for learning, revising, and explaining RAG.
>
> ### ⭐ Core mental model
>
> **Load → Split → Embed → Store → Retrieve → Prompt → Generate**

---

## 📑 Table of Contents

- [1. What is RAG?](#1-what-is-rag)
- [2. The Big Picture](#2-the-big-picture)
- [3. LangChain's Role](#3-langchains-role)
- [4. RAG Components at a Glance](#4-rag-components-at-a-glance)
- [5. Phase A — Knowledge Preparation](#5-phase-a--knowledge-preparation)
  - [5.1 Document Loaders](#51-document-loaders)
  - [5.2 LangChain Document](#52-langchain-document)
  - [5.3 Text Splitters](#53-text-splitters)
  - [5.4 Chunks](#54-chunks)
  - [5.5 Chunk Size](#55-chunk-size)
  - [5.6 Chunk Overlap](#56-chunk-overlap)
  - [5.7 Recursive Character Text Splitter](#57-recursive-character-text-splitter)
  - [5.8 Embeddings](#58-embeddings)
  - [5.9 Document vs Query Embeddings](#59-document-vs-query-embeddings)
  - [5.10 Vector Stores](#510-vector-stores)
- [6. Phase B — Question Answering](#6-phase-b--question-answering)
  - [6.1 User Query](#61-user-query)
  - [6.2 Query Embedding](#62-query-embedding)
  - [6.3 Retrievers](#63-retrievers)
  - [6.4 Similarity Search](#64-similarity-search)
  - [6.5 Top-K Retrieval](#65-top-k-retrieval)
  - [6.6 Similarity Threshold](#66-similarity-threshold)
  - [6.7 MMR](#67-mmr)
  - [6.8 Metadata Filtering](#68-metadata-filtering)
- [7. Context and Prompting](#7-context-and-prompting)
- [8. Complete RAG Chain](#8-complete-rag-chain)
- [9. End-to-End Example](#9-end-to-end-example)
- [10. Important Distinctions](#10-important-distinctions)
- [11. RAG vs Normal LLM](#11-rag-vs-normal-llm)
- [12. Common RAG Failure Points](#12-common-rag-failure-points)
- [13. One-Minute Interview Explanation](#13-one-minute-interview-explanation)
- [14. Final Cheat Sheet](#14-final-cheat-sheet)

---

# 1. What is RAG?

**RAG = Retrieval-Augmented Generation.**

RAG is a technique where an application retrieves relevant information from an external knowledge source and gives that information to an LLM as context before generating an answer.

### Why do we need RAG?

Suppose you have:

```text
company_policy.pdf
```

and the user asks:

> "What is the company's leave policy?"

The LLM does not automatically have access to the contents of your private PDF.

RAG solves this by:

```text
Your Documents
      ↓
Prepare for search
      ↓
Store knowledge
      ↓
User asks question
      ↓
Retrieve relevant information
      ↓
Give information to LLM
      ↓
Generate answer
```

### Simple definition

> **RAG retrieves relevant external knowledge and augments the LLM's prompt with that knowledge before generating the answer.**

---

# 2. The Big Picture

The most important thing to understand is that RAG has **two major phases**.

## Phase A — Knowledge Preparation / Ingestion

Usually performed before users start asking questions.

```text
PDF / CSV / Web
      ↓
Document Loader
      ↓
Documents
      ↓
Text Splitter
      ↓
Chunks
      ↓
Embedding Model
      ↓
Vectors
      ↓
Vector Store
```

## Phase B — Question Answering / Retrieval

Performed when the user asks a question.

```text
User Question
      ↓
Query Embedding
      ↓
Retriever
      ↓
Vector Store
      ↓
Similarity Search
      ↓
Relevant Chunks
      ↓
Context
      ↓
Prompt
      ↓
LLM
      ↓
Final Answer
```

## 🔥 Complete RAG workflow

```text
                         LANGCHAIN RAG
                              │
             ┌────────────────┴────────────────┐
             │                                 │
       KNOWLEDGE FLOW                     QUERY FLOW
       (ingestion)                       (retrieval)
             │                                 │
       PDF / CSV / Web                    User Question
             ↓                                 ↓
     Document Loader                  Query Embedding
             ↓                                 ↓
         Documents                     Retriever
             ↓                                 ↓
      Text Splitter                  Vector Store
             ↓                                 ↓
          Chunks                    Similarity Search
             ↓                                 ↓
        Embeddings                   Top-K Chunks
             ↓                                 │
       Vector Store ───────────────────────────┘
             │
             ↓
      Retrieved Context
             +
        User Question
             ↓
           Prompt
             ↓
            LLM
             ↓
        Final Answer
```

### ⭐ Remember

**The document side prepares the knowledge.**

**The question side finds the knowledge.**

**The LLM side uses the knowledge to generate the answer.**

---

# 3. LangChain's Role

LangChain is a framework for building applications around language models.

It provides abstractions and integrations that help us connect different components.

LangChain is **not**:

- The LLM itself
- The embedding model itself
- The vector database itself
- RAG itself

Instead:

```text
                 LANGCHAIN
                    │
       ┌────────────┼─────────────┐
       ↓            ↓             ↓
    Loaders      Splitters    Retrievers
                                  │
                                  ↓
                            Vector Store
                                  │
                                  ↓
                                 LLM
```

### Important distinction

```text
RAG
 ↓
A technique / architecture

LangChain
 ↓
A framework that helps implement the workflow
```

A good explanation is:

> **RAG describes what the application does: retrieve knowledge and use it for generation. LangChain helps us build and connect the components required for that workflow.**

---

# 4. RAG Components at a Glance

| Component | Main Job | Mental Model |
|---|---|---|
| **Document Loader** | Reads external data | 📥 Bring data in |
| **Document** | Holds content + metadata | 📄 Data container |
| **Text Splitter** | Breaks documents | ✂️ Cut into pieces |
| **Chunk** | Small piece of text | 🧩 Searchable knowledge unit |
| **Embedding Model** | Text → vector | 🔢 Numerical representation |
| **Vector Store** | Stores/searches vectors | 🗄️ Vector-based knowledge storage |
| **Retriever** | Finds relevant documents | 🔎 Knowledge finder |
| **Prompt** | Combines instructions + context + question | 📝 Instructions for LLM |
| **LLM** | Generates response | 🤖 Answer generator |
| **LangChain** | Connects components | 🔗 Application framework |
| **RAG** | Overall retrieval + generation technique | 🧠 Retrieve → Generate |

---

# 5. Phase A — Knowledge Preparation

This phase turns raw external information into a searchable knowledge base.

```text
Raw Data
   ↓
Load
   ↓
Split
   ↓
Embed
   ↓
Store
```

---

## 5.1 Document Loaders

### What is a Document Loader?

A document loader reads information from an external source and converts it into LangChain `Document` objects.

Examples:

```text
PDF
CSV
Web page
Text file
Word document
Database
      ↓
Document Loader
      ↓
LangChain Documents
```

### Mental model

> **Loader = the entry point that brings external knowledge into the application.**

### Common loaders

| Source | Example Loader |
|---|---|
| PDF | `PyPDFLoader` |
| CSV | `CSVLoader` |
| Web page | `WebBaseLoader` |
| Text | `TextLoader` |

The exact loader depends on the source and integration being used.

---

## 5.2 LangChain Document

A LangChain `Document` commonly contains two important parts:

```python
Document(
    page_content="FastAPI is a Python web framework.",
    metadata={"page": 5, "source": "fastapi.pdf"}
)
```

### `page_content`

The actual text:

```text
FastAPI is a Python web framework.
```

### `metadata`

Information about the content:

```python
{
    "page": 5,
    "source": "fastapi.pdf"
}
```

Metadata is useful later for:

- Filtering
- Source tracking
- Citations
- Debugging
- Retrieval constraints

### Loader does NOT create embeddings

```text
Loader
  ↓
Documents
```

Not:

```text
Loader
  ↓
Embeddings
```

---

## 5.3 Text Splitters

### Why split documents?

A large document may contain hundreds of pages.

Sending everything to the LLM for every question would be inefficient and can introduce irrelevant information.

Instead:

```text
Large Document
      ↓
Text Splitter
      ↓
Smaller Chunks
```

Example:

```text
100-page PDF
      ↓
Text Splitter
      ↓
2,000 chunks
```

### Mental model

> **Splitter = cuts a large document into smaller searchable knowledge units.**

---

## 5.4 Chunks

A **chunk** is a smaller piece of the original document.

```text
Large Document
      ↓
┌─────────────┐
│ Chunk 1     │
├─────────────┤
│ Chunk 2     │
├─────────────┤
│ Chunk 3     │
├─────────────┤
│ Chunk 4     │
└─────────────┘
```

Why chunks matter:

```text
Good chunks
    ↓
Better retrieval
    ↓
Better context
    ↓
Potentially better answers
```

Poor chunking can cause important information to be separated or irrelevant information to be retrieved together.

---

## 5.5 Chunk Size

`chunk_size` controls approximately how large a chunk can be.

Example:

```python
RecursiveCharacterTextSplitter(
    chunk_size=500
)
```

Conceptually:

```text
Large text
   ↓
~500-character chunks
```

The exact result depends on the splitter and its separators.

### Important idea

There is no universally perfect chunk size.

The right choice depends on:

- Document structure
- Content type
- Embedding model
- Query patterns
- Desired retrieval granularity

---

## 5.6 Chunk Overlap

Overlap means neighboring chunks share some content.

Example:

```text
Chunk 1:
A B C D E F

Chunk 2:
E F G H I J
```

Here:

```text
E F
```

is the overlap.

### Why overlap?

Suppose an important sentence starts near the end of one chunk and continues into the next.

Without overlap:

```text
Chunk 1 → beginning of idea
Chunk 2 → ending of idea
```

With overlap:

```text
Chunk 1 → beginning + some continuation
Chunk 2 → continuation + next information
```

This can preserve context across boundaries.

### Mental model

> **Chunk overlap = a small bridge between neighboring chunks.**

---

## 5.7 Recursive Character Text Splitter

A commonly used LangChain splitter is:

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)
```

For LangChain `Document` objects:

```python
chunks = splitter.split_documents(documents)
```

### `split_text()`

Used with plain text:

```python
chunks = splitter.split_text(text)
```

### `split_documents()`

Used with `Document` objects:

```python
chunks = splitter.split_documents(documents)
```

Using `split_documents()` allows the resulting chunks to retain useful document metadata.

---

## 5.8 Embeddings

### What is an embedding?

An embedding is a numerical vector representation of text.

```text
Text
 ↓
Embedding Model
 ↓
Vector
```

Example:

```text
"FastAPI is a Python web framework."
              ↓
       Embedding Model
              ↓
 [0.21, 0.73, 0.42, 0.18, ...]
```

The actual vector can contain hundreds or more dimensions depending on the model.

### Mental model

> **Embedding = represent the semantic characteristics of text as numbers so it can be compared computationally.**

---

## 5.9 Why embeddings?

We want semantic search.

Consider:

```text
Query:
"Python API framework"
```

and:

```text
Chunk:
"FastAPI is a modern Python web framework."
```

The wording is not identical, but the meaning is related.

Embeddings allow us to represent both in the same vector space and compare them.

```text
Query
 ↓
Vector

Chunk
 ↓
Vector

Compare vectors
 ↓
Estimate semantic similarity
```

---

## 5.10 Document vs Query Embeddings

There are two sides.

### During ingestion

```text
Document Chunk
      ↓
Embedding Model
      ↓
Document Vector
```

### During retrieval

```text
User Question
      ↓
Embedding Model
      ↓
Query Vector
```

The vectors can then be compared using the vector store's configured similarity/distance mechanism.

### Important

```text
Embedding Model
     ≠
LLM
```

Embedding models are primarily used to represent text for retrieval/search.

LLMs are primarily used to generate language.

---

## 5.11 Vector Stores

### What is a Vector Store?

A vector store stores embeddings and associated information and provides vector-search functionality.

Conceptually:

```text
Chunk
  +
Embedding
  +
Metadata
  ↓
Vector Store
```

Example:

```text
┌─────────────────────────────────────────────┐
│                VECTOR STORE                 │
├─────────────────────────────────────────────┤
│ Vector       │ Text              │ Metadata │
├─────────────────────────────────────────────┤
│ [0.12,...]   │ FastAPI uses...  │ page 2   │
│ [0.81,...]   │ SQL is used...   │ page 5   │
│ [0.33,...]   │ Python is...     │ page 8   │
└─────────────────────────────────────────────┘
```

### Why do we need one?

Suppose we have:

```text
2,000 chunks
```

When a question arrives, we need to find the chunks that are most relevant.

The vector store enables efficient vector-based search.

```text
Query
 ↓
Query Vector
 ↓
Vector Store
 ↓
Search / Compare
 ↓
Rank
 ↓
Relevant Chunks
```

### Common vector stores

Examples:

```text
Chroma
FAISS
Pinecone
```

They differ in deployment, scaling, persistence, indexing, operational model, and features.

---

# 6. Phase B — Question Answering

Once the knowledge base is prepared, users can ask questions.

```text
User Question
      ↓
Retrieve knowledge
      ↓
Build context
      ↓
Ask LLM
      ↓
Answer
```

---

## 6.1 User Query

Suppose the user asks:

```text
"What does FastAPI use for data validation?"
```

This question is the starting point of the retrieval phase.

---

## 6.2 Query Embedding

The question is converted into a vector:

```text
"What does FastAPI use for data validation?"
                    ↓
             Embedding Model
                    ↓
              Query Vector
```

Conceptually:

```text
Query Vector
    ↓
Compare against
stored document vectors
```

---

## 6.3 Retrievers

### What is a Retriever?

A retriever is the component/interface responsible for retrieving relevant documents for a query.

### Mental model

> **Retriever = knowledge finder.**

```text
Question
   ↓
Retriever
   ↓
Relevant Documents
```

### Vector Store vs Retriever

This distinction is extremely important.

#### Vector Store

```text
Stores vectors/data
       +
Performs vector search
```

#### Retriever

```text
Provides a retrieval interface/strategy
       ↓
Returns relevant documents
```

Conceptually:

```text
User Question
      ↓
Retriever
      ↓
Vector Store
      ↓
Similarity Search
      ↓
Relevant Documents
```

A retriever can use a vector store underneath it.

---

## 6.4 Similarity Search

Similarity search asks:

> **Which stored chunks are most similar to this query?**

Conceptually:

```text
User Question
      ↓
Query Embedding
      ↓
Compare with stored vectors
      ↓
Rank candidates
      ↓
Return relevant chunks
```

Example:

```text
Chunk A → 0.92
Chunk B → 0.86
Chunk C → 0.42
Chunk D → 0.31
```

If larger score means greater similarity in the particular system:

```text
A and B
```

are more relevant than C and D.

### ⚠️ Score caveat

Do not assume every vector system uses the same score semantics.

Some systems expose **similarity scores** where higher is better.

Others expose **distance** where lower is better.

Always check the metric/API documentation before interpreting scores or setting thresholds.

---

## 6.5 Top-K Retrieval

`k` controls how many results are requested.

Example:

```python
retriever = vector_store.as_retriever(
    search_kwargs={"k": 3}
)
```

Conceptually:

```text
Question
   ↓
Retriever
   ↓
Top 3 relevant chunks
```

### Why not retrieve everything?

Because too much context can:

- Add irrelevant information
- Increase token usage
- Make prompts larger
- Make it harder for the LLM to focus

### Why not retrieve only one?

The answer may depend on multiple pieces of information.

Therefore, `k` is an important retrieval parameter.

---

## 6.6 Similarity Threshold

Normal top-k retrieval asks:

> Give me the top `k` results.

But what if none of them are actually relevant?

Example:

```text
0.92
0.86
0.41
0.30
```

A threshold can conceptually enforce:

> Return results only when they meet an acceptable similarity criterion.

For example, if the system's score is a similarity score and the threshold is:

```text
0.80
```

then:

```text
0.92 → keep
0.86 → keep
0.41 → reject
0.30 → reject
```

### Mental model

```text
Similarity Search
      ↓
Find the closest results

Similarity + Threshold
      ↓
Find results that are close enough
```

### Important

Threshold behavior and score direction depend on the specific vector store, metric, and retriever configuration.

---

## 6.7 MMR

**MMR = Maximum Marginal Relevance.**

MMR attempts to balance:

```text
Relevance
    +
Diversity
```

Why?

Imagine retrieval returns:

```text
Chunk A → FastAPI validation
Chunk B → FastAPI validation
Chunk C → FastAPI validation
```

All may be highly similar, but they may repeat the same information.

MMR can try to select:

```text
Chunk A → validation
Chunk B → request models
Chunk C → error handling
```

provided those chunks are relevant to the query.

### Mental model

```text
Similarity Search
→ Most similar chunks

MMR
→ Relevant + less redundant chunks
```

---

## 6.8 Metadata Filtering

Metadata contains information about the source or category of a chunk.

Example:

```python
{
    "source": "fastapi.pdf",
    "page": 5,
    "topic": "validation"
}
```

Metadata can help with:

- Source tracking
- Filtering
- Citations
- Debugging
- Restricting retrieval

Conceptually:

```text
User Question
      +
Metadata Filter
      ↓
Retriever
      ↓
Vector Store
      ↓
Relevant Chunks
```

Example idea:

```text
topic = "FastAPI"
```

This can restrict retrieval to matching metadata where the chosen vector store/retriever supports that filter.

---

# 7. Context and Prompting

This is where **retrieval meets generation**.

After retrieval, we have:

```text
Document 1
Document 2
Document 3
```

We need to turn their content into usable context.

```text
Retrieved Documents
       ↓
Format / Combine
       ↓
Context
```

Then combine:

```text
Instructions
      +
Retrieved Context
      +
User Question
      ↓
Prompt
```

### Conceptual RAG prompt

```text
Answer the question using the provided context.

Context:
{retrieved_context}

Question:
{question}
```

The exact prompt can be designed differently depending on the application.

### Core idea

> **The LLM is given both the user's question and relevant retrieved knowledge.**

---

# 8. Complete RAG Chain

Now everything connects.

```text
                         RAG APPLICATION
                               │
                               │
                ┌──────────────┴──────────────┐
                │                             │
          INGESTION PHASE                QUERY PHASE
                │                             │
          PDF / CSV / Web               User Question
                ↓                             ↓
        Document Loader              Query Embedding
                ↓                             ↓
            Documents                     Retriever
                ↓                             ↓
         Text Splitter                 Vector Store
                ↓                             ↓
             Chunks                  Similarity Search
                ↓                             ↓
          Embedding Model              Top-K Chunks
                ↓                             │
          Vector Store                       │
                │                             │
                └──────────────┬──────────────┘
                               ↓
                      Retrieved Context
                               +
                         User Question
                               ↓
                            Prompt
                               ↓
                              LLM
                               ↓
                         Final Answer
```

---

# 9. End-to-End Example

Suppose we have:

```text
fastapi.pdf
```

Inside the PDF:

```text
FastAPI uses Pydantic models for data validation.
```

---

## Step 1 — Load

```text
fastapi.pdf
      ↓
PyPDFLoader
      ↓
Documents
```

---

## Step 2 — Split

```text
Documents
      ↓
Text Splitter
      ↓
Chunks
```

One chunk may contain:

```text
FastAPI uses Pydantic models for data validation.
```

---

## Step 3 — Embed

```text
Chunk
      ↓
Embedding Model
      ↓
[0.23, 0.81, 0.42, ...]
```

---

## Step 4 — Store

```text
Chunk
 +
Vector
 +
Metadata
      ↓
Chroma
```

The knowledge base is now ready.

---

## Step 5 — User asks

```text
"What does FastAPI use for data validation?"
```

---

## Step 6 — Query embedding

```text
Question
   ↓
Embedding Model
   ↓
Query Vector
```

---

## Step 7 — Retrieve

```text
Query Vector
      ↓
Retriever
      ↓
Vector Store
      ↓
Similarity Search
      ↓
Relevant Chunk
```

Retrieved:

```text
"FastAPI uses Pydantic models for data validation."
```

---

## Step 8 — Build context

```text
Retrieved Chunk
      ↓
Context
```

---

## Step 9 — Build prompt

```text
Instructions
      +
Context
      +
Question
      ↓
Prompt
```

---

## Step 10 — LLM

```text
Prompt
  ↓
LLM
```

---

## Step 11 — Answer

```text
"FastAPI uses Pydantic models to validate data."
```

---

# 10. Important Distinctions

These distinctions are very useful for interviews and debugging.

## Loader vs Splitter

```text
Loader
→ Gets data into the application

Splitter
→ Breaks loaded data into chunks
```

---

## Splitter vs Embedding

```text
Splitter
→ Text → Smaller text

Embedding
→ Text → Vector
```

---

## Embedding vs Vector Store

```text
Embedding Model
→ Creates vectors

Vector Store
→ Stores/searches vectors
```

---

## Vector Store vs Retriever

```text
Vector Store
→ Vector storage + search capability

Retriever
→ Retrieval interface/strategy
```

---

## Retriever vs LLM

```text
Retriever
→ Finds relevant knowledge

LLM
→ Generates language
```

---

## RAG vs LangChain

```text
RAG
→ Retrieval + generation technique

LangChain
→ Framework for building/connecting application components
```

---

# 11. RAG vs Normal LLM

## Without RAG

```text
User Question
      ↓
     LLM
      ↓
    Answer
```

The LLM answers using its available model knowledge and the information in the current prompt/conversation.

---

## With RAG

```text
User Question
      ↓
    Retrieve
      ↓
Relevant Context
      ↓
Question + Context
      ↓
     LLM
      ↓
    Answer
```

### The key difference

> **RAG adds an external knowledge retrieval step before generation.**

---

# 12. Common RAG Failure Points

A RAG system is a pipeline.

A useful debugging model is:

```text
Bad Source
    ↓
Bad Loading
    ↓
Bad Chunking
    ↓
Bad Embeddings
    ↓
Bad Retrieval
    ↓
Bad Context
    ↓
Bad Prompt
    ↓
Bad Answer
```

So if the answer is wrong, don't immediately blame the LLM.

Check each stage.

### 1. Loading problem

Did the loader extract the document correctly?

### 2. Chunking problem

Are important ideas being split apart?

### 3. Embedding problem

Is the embedding model appropriate for the content and language?

### 4. Retrieval problem

Did the retriever actually find the right chunks?

### 5. Context problem

Was useful information lost or overwhelmed by irrelevant information?

### 6. Prompt problem

Did the prompt clearly tell the LLM how to use the context?

### 7. Generation problem

Did the LLM correctly use the supplied context?

---

# 13. One-Minute Interview Explanation

> **RAG, or Retrieval-Augmented Generation, is a technique used to ground an LLM's responses with external knowledge. In a LangChain RAG application, data such as PDFs, CSVs, or web pages is loaded using document loaders and split into smaller chunks. The chunks are converted into embeddings and stored in a vector store. When a user asks a question, the question is embedded and passed through a retriever, which searches the vector store and returns relevant chunks. Those chunks are formatted as context along with the user's question and instructions. The resulting prompt is then sent to an LLM, which generates the final answer using the retrieved context.**

### Shorter version

> **Load the documents, split them into chunks, embed and store the chunks, retrieve the relevant chunks for a question, add them to the prompt, and let the LLM generate the answer.**

---

# 14. Final Cheat Sheet

## 🔥 The 7-step RAG formula

```text
1. LOAD
   ↓
2. SPLIT
   ↓
3. EMBED
   ↓
4. STORE
   ↓
5. RETRIEVE
   ↓
6. PROMPT
   ↓
7. GENERATE
```

### What each means

```text
LOAD
→ Bring external data into the application

SPLIT
→ Break large documents into chunks

EMBED
→ Convert chunks into vectors

STORE
→ Put vectors + associated information into a vector store

RETRIEVE
→ Find relevant chunks for the user question

PROMPT
→ Combine instructions + context + question

GENERATE
→ LLM produces the final response
```

---

## 🧠 Ultimate Mental Model

```text
                 YOUR KNOWLEDGE
                       │
                ┌──────▼──────┐
                │    LOAD     │
                └──────┬──────┘
                       ↓
                ┌─────────────┐
                │    SPLIT    │
                └──────┬──────┘
                       ↓
                   CHUNKS
                       │
                       ↓
                ┌─────────────┐
                │    EMBED    │
                └──────┬──────┘
                       ↓
                  VECTORS
                       │
                       ↓
                ┌─────────────┐
                │    STORE    │
                │ Vector Store│
                └──────┬──────┘
                       │
                       │
                       │
                  USER QUESTION
                       │
                       ↓
                ┌─────────────┐
                │    EMBED    │
                └──────┬──────┘
                       ↓
                 QUERY VECTOR
                       │
                       ↓
                ┌─────────────┐
                │  RETRIEVE   │
                └──────┬──────┘
                       ↓
                VECTOR SEARCH
                       ↓
                RELEVANT CHUNKS
                       │
                       ↓
              ┌─────────────────┐
              │ QUESTION +      │
              │ CONTEXT +       │
              │ INSTRUCTIONS    │
              └────────┬────────┘
                       ↓
                    PROMPT
                       │
                       ↓
                     LLM
                       │
                       ↓
                 FINAL ANSWER
```

---

## 🎯 One sentence to remember forever

> **RAG prepares your knowledge for semantic search, retrieves the relevant pieces when a user asks a question, and gives those pieces to an LLM so it can generate a context-aware answer.**

---

## 🛠️ Typical LangChain Components

A practical LangChain RAG application may use components such as:

```python
# Loading
PyPDFLoader

# Splitting
RecursiveCharacterTextSplitter

# Embeddings
HuggingFaceEmbeddings

# Vector Store
Chroma

# Retrieval
vector_store.as_retriever()

# Prompt
ChatPromptTemplate

# LLM
Chat model / LLM integration
```

The exact imports and APIs can vary by LangChain version and provider.

---

## 📌 Revision Formula

Whenever you forget RAG, ask these questions:

```text
1. Where does my knowledge come from?
             ↓
        Document Loader

2. How do I break it down?
             ↓
        Text Splitter

3. How do I represent meaning?
             ↓
        Embeddings

4. Where do I keep/search it?
             ↓
        Vector Store

5. How do I find relevant knowledge?
             ↓
        Retriever

6. How do I give that knowledge to the model?
             ↓
        Context + Prompt

7. Who generates the answer?
             ↓
        LLM
```

That is the complete **LangChain RAG mental model**.
