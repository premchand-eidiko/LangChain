from __future__ import annotations

from typing import List
from uuid import UUID

from langchain_core.documents import Document

from app.rag.loaders import load_document
from app.rag.splitter import split_documents
from app.rag.vectorstore import UserVectorStore, vector_store


def index_document(
    path: str,
    user_id: UUID,
    document_id: UUID,
    store: UserVectorStore = vector_store,
) -> int:
    source_documents = load_document(path)
    chunks = split_documents(source_documents, user_id, document_id)
    if not chunks:
        raise ValueError("The document produced no searchable chunks")
    store.add_chunks(user_id, chunks)
    return len(chunks)
