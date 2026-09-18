from __future__ import annotations

from pathlib import Path
from typing import List, Optional
from uuid import UUID, uuid4

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import Document


ALLOWED_FILE_TYPES = {".pdf", ".docx", ".txt", ".csv"}
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
