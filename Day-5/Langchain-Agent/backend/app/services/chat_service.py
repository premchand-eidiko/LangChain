from __future__ import annotations

from pathlib import Path
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Chat, ChatDocument, Document, Message


def create_chat(db: Session, user_id: UUID, title: str) -> Chat:
    chat = Chat(user_id=user_id, title=title)
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat


def list_user_chats(db: Session, user_id: UUID) -> List[Chat]:
    statement = (
        select(Chat)
        .where(Chat.user_id == user_id)
        .order_by(Chat.updated_at.desc())
    )
    return list(db.scalars(statement).all())


def get_user_chat(db: Session, user_id: UUID, chat_id: UUID) -> Optional[Chat]:
    statement = (
        select(Chat)
        .options(selectinload(Chat.messages))
        .where(Chat.id == chat_id, Chat.user_id == user_id)
    )
    return db.scalar(statement)


def delete_user_chat(db: Session, user_id: UUID, chat_id: UUID) -> bool:
    chat = get_user_chat(db, user_id, chat_id)
    if chat is None:
        return False

    document_ids = list(
        db.scalars(
            select(ChatDocument.document_id).where(ChatDocument.chat_id == chat_id)
        ).all()
    )
    db.delete(chat)
    db.commit()

    if document_ids:
        orphaned_documents = list(
            db.scalars(
                select(Document).where(
                    Document.user_id == user_id,
                    Document.id.in_(document_ids),
                    ~Document.chat_documents.any(),
                )
            ).all()
        )
        for document in orphaned_documents:
            Path(document.storage_path).unlink(missing_ok=True)
            db.delete(document)
        db.commit()
    return True


def rename_user_chat(db: Session, user_id: UUID, chat_id: UUID, title: str) -> Optional[Chat]:
    chat = get_user_chat(db, user_id, chat_id)
    if chat is None:
        return None
    chat.title = title
    db.commit()
    db.refresh(chat)
    return chat


def add_message(
    db: Session,
    user_id: UUID,
    chat_id: UUID,
    role: str,
    content: str,
) -> Optional[Message]:
    chat = get_user_chat(db, user_id, chat_id)
    if chat is None:
        return None
    message = Message(chat_id=chat.id, role=role, content=content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message
