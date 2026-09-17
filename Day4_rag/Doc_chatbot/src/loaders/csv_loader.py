"""CSV loading helpers."""

from pathlib import Path

from langchain_community.document_loaders import CSVLoader
from langchain_core.documents import Document


def load_csv(path: Path) -> list[Document]:
    """Load one CSV as LangChain documents, retaining the source path."""
    documents = CSVLoader(str(path)).load()
    for document in documents:
        document.page_content = (
            f"CSV file: {path.name}\n\n{document.page_content}"
        )
    return documents
