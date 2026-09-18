from __future__ import annotations

from pathlib import Path
from typing import List, Optional
from uuid import UUID

from pypdf import PdfReader
from langchain_core.documents import Document as LangChainDocument
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.rag.retriever import retrieve_user_document_chunks
from app.rag.vectorstore import UserVectorStore, vector_store
from app.services.document_service import (
    get_user_document,
    get_user_document_by_filename,
)


class DocumentSearchInput(BaseModel):
    document_id: Optional[UUID] = Field(
        default=None, description="Internal ID of the uploaded document, if known"
    )
    filename: Optional[str] = Field(
        default=None, description="Original uploaded filename, if known"
    )
    query: str = Field(min_length=1, max_length=2000)


def _format_results(results: List[LangChainDocument]) -> str:
    if not results:
        return "No relevant content was found in that document."
    sections = []
    for index, result in enumerate(results, start=1):
        source = result.metadata.get("source", "uploaded document")
        sections.append("[Source {}: {}]\n{}".format(index, source, result.page_content))
    return "\n\n".join(sections)


def build_document_search_tool(
    db: Session,
    user_id: UUID,
    store: UserVectorStore = vector_store,
) -> StructuredTool:
    """Build a document tool bound to one authenticated user's identity."""

    def search_document(
        query: str,
        document_id: Optional[UUID] = None,
        filename: Optional[str] = None,
    ) -> str:
        if document_id is None and not filename:
            return "Please provide the uploaded document filename."
        document = (
            get_user_document(db, user_id, document_id)
            if document_id is not None
            else get_user_document_by_filename(db, user_id, filename or "")
        )
        if document is None:
            return "The requested document was not found."

        if (
            document.file_type.lower() == "pdf"
            and any(word in query.lower() for word in ("page", "pages"))
        ):
            try:
                page_count = len(PdfReader(Path(document.storage_path)).pages)
                return "{} has {} page{}.".format(
                    document.filename, page_count, "" if page_count == 1 else "s"
                )
            except Exception:
                return "I could not determine the page count for that PDF."

        results = retrieve_user_document_chunks(
            user_id=user_id,
            document_id=document.id,
            query=query,
            store=store,
        )
        return _format_results(results)

    return StructuredTool.from_function(
        func=search_document,
        name="document_search",
        description=(
            "Search one document uploaded by the authenticated user. "
            "Use the original filename when the user names a document. "
            "Use this for questions about uploaded document content, including "
            "PDF page-count questions."
        ),
        args_schema=DocumentSearchInput,
    )