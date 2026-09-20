from __future__ import annotations

from pathlib import Path
import re
from typing import List, Optional
from uuid import UUID

from pypdf import PdfReader
from pptx import Presentation
from langchain_core.documents import Document as LangChainDocument
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.rag.retriever import retrieve_user_document_chunks
from app.rag.loaders import load_document
from app.rag.vectorstore import UserVectorStore, vector_store
from app.services.document_service import (
    get_user_document,
    get_user_document_by_filename,
    list_chat_documents,
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
        source = Path(source).name if ":\\" in source or "/" in source else source
        sections.append("[Source {}: {}]\n{}".format(index, source, result.page_content))
    return "\n\n".join(sections)


def build_document_search_tool(
    db: Session,
    user_id: UUID,
    store: UserVectorStore = vector_store,
    chat_id: Optional[UUID] = None,
) -> StructuredTool:
    """Build a document tool bound to one authenticated user's identity."""

    def search_document(
        query: str,
        document_id: Optional[UUID] = None,
        filename: Optional[str] = None,
    ) -> str:
        if document_id is None and not filename:
            if chat_id is not None:
                documents = list_chat_documents(db, user_id, chat_id)
                if not documents:
                    return "No documents have been uploaded in this chat."
                if len(documents) == 1:
                    document = documents[0]
                else:
                    return "Multiple documents are uploaded in this chat. Please provide the filename you want me to search.\n" + "\n".join(
                        f"- {document.filename}" for document in documents
                    )
            else:
                return "Please provide the uploaded document filename."
        else:
            document = (
                get_user_document(db, user_id, document_id)
                if document_id is not None
                else get_user_document_by_filename(db, user_id, filename or "")
            )
        if document is None:
            return "The requested document was not found."

        if chat_id is not None and document not in list_chat_documents(db, user_id, chat_id):
            return "That document is not uploaded in this chat."

        if any(word in query.lower() for word in ("page", "pages")):
            try:
                if document.file_type.lower() == "pdf":
                    count = len(PdfReader(Path(document.storage_path)).pages)
                    unit = "page"
                elif document.file_type.lower() == "pptx":
                    count = len(Presentation(document.storage_path).slides)
                    unit = "slide"
                else:
                    count = None
                if count is not None:
                    return "{} has {} {}{}.".format(
                        document.filename, count, unit, "" if count == 1 else "s"
                    )
            except Exception:
                return "I could not determine the page or slide count for that document."

        if any(
            phrase in query.lower()
            for phrase in ("author", "written by", "created by", "presented by")
        ):
            try:
                opening_pages = load_document(document.storage_path)[:2]
                for page in opening_pages:
                    lines = page.page_content.splitlines()
                    for index, line in enumerate(lines):
                        if re.search(r"\b1st\b", line, re.IGNORECASE):
                            author_line = " ".join(lines[index : index + 3])
                            author_line = author_line[author_line.lower().find("1st") :]
                            return (
                                f"The authors of {document.filename} are listed as: "
                                + re.sub(r"\s+", " ", author_line).strip()
                            )
            except Exception:
                pass

        results = retrieve_user_document_chunks(
            user_id=user_id,
            document_id=document.id,
            query=query,
            store=store,
        )
        if not results and any(
            phrase in query.lower()
            for phrase in ("author", "written by", "created by", "presented by")
        ):
            try:
                source_documents = load_document(document.storage_path)
                results = source_documents[:4]
            except Exception:
                results = []
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