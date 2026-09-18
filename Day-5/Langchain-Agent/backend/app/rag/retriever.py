from __future__ import annotations

from typing import List
from uuid import UUID

from langchain_core.documents import Document

from app.rag.vectorstore import UserVectorStore, vector_store


def retrieve_user_document_chunks(
    user_id: UUID,
    document_id: UUID,
    query: str,
    k: int = 4,
    store: UserVectorStore = vector_store,
) -> List[Document]:
    if not query.strip():
        raise ValueError("A retrieval query is required")
    results = store.search(user_id, query, k=k)
    return [
        document
        for document in results
        if document.metadata.get("user_id") == str(user_id)
        and document.metadata.get("document_id") == str(document_id)
    ]
