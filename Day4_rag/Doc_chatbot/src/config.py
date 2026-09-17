"""Central configuration for ingestion, retrieval, and chat."""

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
PDF_DIR = DATA_DIR / "pdf"
CSV_DIR = DATA_DIR / "csv"
URLS_FILE = DATA_DIR / "web" / "urls.txt"
VECTOR_STORE_DIR = PROJECT_ROOT / "vector_store"

load_dotenv(PROJECT_ROOT / ".env")

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
RETRIEVAL_K = int(os.getenv("RETRIEVAL_K", "4"))
EMBEDDING_MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2"
)
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")


def load_environment() -> None:
    """Load values from the project .env file, if it exists."""
    load_dotenv(PROJECT_ROOT / ".env")
