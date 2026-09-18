from __future__ import annotations

from typing import List
from uuid import UUID

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=120,
    separators=["\n\n", "\n", ". ", " ", ""],
)


def split_documents(
    documents: List[Document], user_id: UUID, document_id: UUID
) -> List[Document]:
    chunks = _splitter.split_documents(documents)
    for index, chunk in enumerate(chunks):
        chunk.metadata.update(
            {
                "user_id": str(user_id),
                "document_id": str(document_id),
                "chunk_index": index,
            }
        )
    return chunks
