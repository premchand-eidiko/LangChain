from __future__ import annotations

from typing import Dict, List
from uuid import UUID

from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore

from app.rag.embeddings import DevelopmentEmbeddings


class UserVectorStore:
    def __init__(self) -> None:
        self._stores: Dict[str, InMemoryVectorStore] = {}
        self._embeddings = DevelopmentEmbeddings()

    def _get_store(self, user_id: UUID) -> InMemoryVectorStore:
        key = str(user_id)
        if key not in self._stores:
            self._stores[key] = InMemoryVectorStore(self._embeddings)
        return self._stores[key]

    def add_chunks(self, user_id: UUID, chunks: List[Document]) -> List[str]:
        return self._get_store(user_id).add_documents(chunks)

    def search(self, user_id: UUID, query: str, k: int = 4) -> List[Document]:
        return self._get_store(user_id).similarity_search(query, k=k)


vector_store = UserVectorStore()
