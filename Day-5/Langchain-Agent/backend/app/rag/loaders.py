from __future__ import annotations

import csv
from pathlib import Path
from typing import List

from langchain_community.document_loaders import (
    CSVLoader,
    Docx2txtLoader,
    PyPDFLoader,
    TextLoader,
)
from langchain_core.documents import Document as LangChainDocument


LOADERS = {
    ".pdf": PyPDFLoader,
    ".docx": Docx2txtLoader,
    ".txt": TextLoader,
    ".csv": CSVLoader,
}


def load_document(path: str) -> List[LangChainDocument]:
    file_path = Path(path)
    loader_class = LOADERS.get(file_path.suffix.lower())
    if loader_class is None:
        raise ValueError("Unsupported document type")
    loader = loader_class(str(file_path))
    documents = loader.load()
    if file_path.suffix.lower() == ".csv" and not documents:
        with file_path.open(newline="", encoding="utf-8-sig") as csv_file:
            rows = [", ".join(row) for row in csv.reader(csv_file) if any(row)]
        documents = [LangChainDocument(page_content="\n".join(rows))] if rows else []
    if not any(document.page_content.strip() for document in documents):
        raise ValueError("The document contains no readable text")
    return documents
