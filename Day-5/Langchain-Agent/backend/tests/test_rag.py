from uuid import uuid4

from langchain_core.documents import Document

from app.rag.embeddings import DevelopmentEmbeddings
from app.rag.retriever import retrieve_user_document_chunks
from app.rag.splitter import split_documents
from app.rag.vectorstore import UserVectorStore


def test_splitter_adds_ownership_metadata():
    user_id = uuid4()
    document_id = uuid4()
    chunks = split_documents(
        [Document(page_content="Annual leave is twenty days.")],
        user_id,
        document_id,
    )

    assert len(chunks) == 1
    assert chunks[0].metadata["user_id"] == str(user_id)
    assert chunks[0].metadata["document_id"] == str(document_id)
    assert chunks[0].metadata["chunk_index"] == 0


def test_retriever_filters_by_user_and_document():
    store = UserVectorStore()
    owner_id = uuid4()
    other_user_id = uuid4()
    document_id = uuid4()
    other_document_id = uuid4()
    store.add_chunks(
        owner_id,
        [
            Document(
                page_content="Owner policy: twenty annual leave days.",
                metadata={
                    "user_id": str(owner_id),
                    "document_id": str(document_id),
                },
            ),
            Document(
                page_content="Owner private document.",
                metadata={
                    "user_id": str(owner_id),
                    "document_id": str(other_document_id),
                },
            ),
        ],
    )
    store.add_chunks(
        other_user_id,
        [
            Document(
                page_content="Other user's confidential policy.",
                metadata={
                    "user_id": str(other_user_id),
                    "document_id": str(document_id),
                },
            )
        ],
    )

    results = retrieve_user_document_chunks(
        owner_id, document_id, "How many annual leave days?", store=store
    )
    assert len(results) == 1
    assert "twenty" in results[0].page_content
    assert retrieve_user_document_chunks(
        owner_id, other_document_id, "confidential", store=store
    )[0].metadata["document_id"] == str(other_document_id)
    assert retrieve_user_document_chunks(
        other_user_id, document_id, "policy", store=store
    )[0].metadata["user_id"] == str(other_user_id)


def test_development_embeddings_are_deterministic():
    embeddings = DevelopmentEmbeddings()
    assert embeddings.embed_query("same text") == embeddings.embed_query("same text")
    assert len(embeddings.embed_query("same text")) == 64
