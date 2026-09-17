"""Build retrievers independently from the storage implementation."""

from langchain_core.retrievers import BaseRetriever


def create_retriever(vector_store, k: int = 4) -> BaseRetriever:
    """Create a similarity retriever with configurable top-k results."""
    return vector_store.as_retriever(search_type="similarity", search_kwargs={"k": k})
