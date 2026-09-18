from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Chat, Message


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
    db.delete(chat)
    db.commit()
    return True


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
