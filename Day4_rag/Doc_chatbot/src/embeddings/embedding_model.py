"""Create the single embedding model used by ingestion and search."""

from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings

from src.config import EMBEDDING_MODEL_NAME


@lru_cache(maxsize=1)
def get_embedding_model() -> HuggingFaceEmbeddings:
    """Return one cached Hugging Face embedding model instance."""
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
