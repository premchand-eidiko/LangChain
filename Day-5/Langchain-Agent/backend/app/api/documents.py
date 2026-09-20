from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from typing_extensions import Annotated

from app.api.dependencies import get_current_user
from app.services.chat_service import get_user_chat
from app.database.session import get_db
from app.models import Document, User
from app.rag.pipeline import index_document
from app.schemas.document import DocumentResponse
from app.services.document_service import (
    MAX_FILE_SIZE,
    delete_user_document,
    attach_document_to_chat,
    list_user_documents,
    save_document,
    validate_filename,
)


router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentResponse, status_code=201)
def upload_document(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    upload: UploadFile = File(...),
    chat_id: UUID | None = Form(default=None),
) -> Document:
    try:
        extension = validate_filename(upload.filename)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    content = upload.file.read(MAX_FILE_SIZE + 1)
    if not content:
        raise HTTPException(status_code=400, detail="The uploaded file is empty")
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="The file exceeds the 10 MB limit")

    if chat_id is not None:
        if get_user_chat(db, current_user.id, chat_id) is None:
            raise HTTPException(status_code=404, detail="Chat not found")

    document = save_document(db, current_user.id, upload, extension, content)
    if chat_id is not None:
        attach_document_to_chat(db, current_user.id, chat_id, document.id)
    try:
        index_document(
            document.storage_path,
            current_user.id,
            document.id,
        )
    except Exception as error:
        delete_user_document(db, current_user.id, document.id)
        raise HTTPException(
            status_code=422,
            detail="The document could not be processed for search",
        ) from error
    return document


@router.get("", response_model=List[DocumentResponse])
def list_documents(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> List[Document]:
    return list_user_documents(db, current_user.id)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_document(
    document_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    if not delete_user_document(db, current_user.id, document_id):
        raise HTTPException(status_code=404, detail="Document not found")
