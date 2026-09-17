"""PDF loading helpers."""

from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document


def load_pdf(path: Path) -> list[Document]:
    """Load one PDF while preserving page and source metadata."""
    documents = PyPDFLoader(str(path)).load()
    for document in documents:
        author = document.metadata.get("author", "Unknown")
        document.page_content = (
            f"PDF file: {path.name}\nAuthor: {author}\n\n{document.page_content}"
        )
    return documents
