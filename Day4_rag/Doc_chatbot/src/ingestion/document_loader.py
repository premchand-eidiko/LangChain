"""Central pipeline for loading all configured document sources."""

from dataclasses import dataclass, field
from pathlib import Path

from langchain_core.documents import Document

from src.loaders.csv_loader import load_csv
from src.loaders.pdf_loader import load_pdf
from src.loaders.web_loader import load_web_page


@dataclass
class LoadedDocuments:
    """Documents plus simple counts useful for CLI reporting."""

    documents: list[Document] = field(default_factory=list)
    pdf_count: int = 0
    csv_count: int = 0
    web_count: int = 0


def _load_many(paths: list[Path], loader, label: str) -> list[Document]:
    documents: list[Document] = []
    for path in paths:
        try:
            documents.extend(loader(path))
        except Exception as error:
            print(f"Could not load {label} '{path.name}': {error}")
    return documents


def load_all_documents(
    pdf_dir: Path, csv_dir: Path, urls_file: Path
) -> LoadedDocuments:
    """Load PDFs, CSVs, and URLs from the project data directories."""
    pdf_documents = _load_many(sorted(pdf_dir.glob("*.pdf")), load_pdf, "PDF")
    csv_documents = _load_many(sorted(csv_dir.glob("*.csv")), load_csv, "CSV")
    web_documents: list[Document] = []
    if urls_file.exists():
        urls = [
            line.strip()
            for line in urls_file.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]
        for url in urls:
            try:
                web_documents.extend(load_web_page(url))
            except Exception as error:
                print(f"Could not load URL '{url}': {error}")
    return LoadedDocuments(
        documents=pdf_documents + csv_documents + web_documents,
        pdf_count=len(pdf_documents),
        csv_count=len(csv_documents),
        web_count=len(web_documents),
    )
