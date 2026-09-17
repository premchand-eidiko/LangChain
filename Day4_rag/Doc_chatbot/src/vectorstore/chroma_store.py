"""Persistence and search operations for Chroma."""

import sys
from pathlib import Path

try:
    import pysqlite3
except ImportError:
    pysqlite3 = None
else:
    sys.modules["sqlite3"] = pysqlite3

from langchain_chroma import Chroma
from langchain_core.documents import Document

from src.embeddings.embedding_model import get_embedding_model


def create_vector_store(
    documents: list[Document], persist_directory: Path
) -> Chroma:
    """Create a persistent Chroma collection from document chunks."""
    persist_directory.mkdir(parents=True, exist_ok=True)
    return Chroma.from_documents(
        documents=documents,
        embedding=get_embedding_model(),
        persist_directory=str(persist_directory),
    )


def load_vector_store(persist_directory: Path) -> Chroma:
    """Open an existing persistent Chroma collection."""
    if not persist_directory.exists():
        raise FileNotFoundError(
            f"Vector store not found at {persist_directory}. Run 'python run.py ingest' first."
        )
    return Chroma(
        persist_directory=str(persist_directory), embedding_function=get_embedding_model()
    )


def similarity_search(
    vector_store: Chroma, query: str, k: int = 4
) -> list[Document]:
    """Return the most similar documents for a query."""
    return vector_store.similarity_search(query, k=k)
