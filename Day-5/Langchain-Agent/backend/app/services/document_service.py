from __future__ import annotations

from pathlib import Path
from typing import List, Optional
from uuid import UUID, uuid4

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import Document
from app.models import ChatDocument


ALLOWED_FILE_TYPES = {".pdf", ".docx", ".pptx", ".txt", ".csv"}
MAX_FILE_SIZE = 10 * 1024 * 1024


def get_upload_directory() -> Path:
    directory = Path(get_settings().upload_dir)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def validate_filename(filename: Optional[str]) -> str:
    if not filename:
        raise ValueError("A filename is required")
    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_FILE_TYPES:
        allowed = ", ".join(sorted(ALLOWED_FILE_TYPES))
        raise ValueError("Unsupported file type. Allowed types: " + allowed)
    return extension


def save_document(
    db: Session,
    user_id: UUID,
    upload: UploadFile,
    extension: str,
    content: bytes,
) -> Document:
    document_id = uuid4()
    stored_path = get_upload_directory() / (str(document_id) + extension)
    stored_path.write_bytes(content)

    document = Document(
        id=document_id,
        user_id=user_id,
        filename=upload.filename or (str(document_id) + extension),
        file_type=extension.lstrip("."),
        storage_path=str(stored_path),
    )
    try:
        db.add(document)
        db.commit()
        db.refresh(document)
    except Exception:
        db.rollback()
        stored_path.unlink(missing_ok=True)
        raise
    return document


def list_user_documents(db: Session, user_id: UUID) -> List[Document]:
    statement = (
        select(Document)
        .where(Document.user_id == user_id)
        .order_by(Document.created_at.desc())
    )
    return list(db.scalars(statement).all())


def attach_document_to_chat(db: Session, user_id: UUID, chat_id: UUID, document_id: UUID) -> bool:
    statement = select(ChatDocument).join(ChatDocument.document).where(
        ChatDocument.chat_id == chat_id,
        ChatDocument.document_id == document_id,
        Document.user_id == user_id,
    )
    if db.scalar(statement) is not None:
        return True
    db.add(ChatDocument(chat_id=chat_id, document_id=document_id))
    db.commit()
    return True


def list_chat_documents(db: Session, user_id: UUID, chat_id: UUID) -> List[Document]:
    statement = (
        select(Document)
        .join(ChatDocument, ChatDocument.document_id == Document.id)
        .where(ChatDocument.chat_id == chat_id, Document.user_id == user_id)
        .order_by(ChatDocument.created_at.asc())
    )
    documents = list(db.scalars(statement).all())
    unique_documents = {}
    for document in documents:
        unique_documents[document.filename.casefold()] = document
    return list(unique_documents.values())


def get_user_document(
    db: Session, user_id: UUID, document_id: UUID
) -> Optional[Document]:
    statement = select(Document).where(
        Document.id == document_id, Document.user_id == user_id
    )
    return db.scalar(statement)


def get_user_document_by_filename(
    db: Session, user_id: UUID, filename: str
) -> Optional[Document]:
    statement = select(Document).where(
        Document.user_id == user_id,
        Document.filename.ilike(filename.strip()),
    )
    return db.scalar(statement)


def delete_user_document(db: Session, user_id: UUID, document_id: UUID) -> bool:
    document = get_user_document(db, user_id, document_id)
    if document is None:
        return False
    Path(document.storage_path).unlink(missing_ok=True)
    db.delete(document)
    db.commit()
    return True
