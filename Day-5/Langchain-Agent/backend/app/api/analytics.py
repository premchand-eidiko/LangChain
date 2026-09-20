from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import distinct, func, select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.database.session import get_db
from app.models import Chat, ChatDocument, Document, User


router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/usage")
def usage_summary(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    user_count = db.scalar(select(func.count(User.id))) or 0
    chat_count = db.scalar(select(func.count(Chat.id))) or 0
    document_count = db.scalar(select(func.count(Document.id))) or 0

    user_rows = db.execute(
        select(
            User.id,
            User.email,
            func.count(distinct(Chat.id)).label("chat_count"),
            func.count(distinct(Document.id)).label("document_count"),
        )
        .outerjoin(Chat, Chat.user_id == User.id)
        .outerjoin(Document, Document.user_id == User.id)
        .group_by(User.id, User.email)
        .order_by(User.email.asc())
    ).all()

    chat_rows = db.execute(
        select(
            Chat.id,
            Chat.title,
            Chat.user_id,
            func.count(distinct(ChatDocument.document_id)).label("document_count"),
        )
        .outerjoin(ChatDocument, ChatDocument.chat_id == Chat.id)
        .group_by(Chat.id, Chat.title, Chat.user_id)
        .order_by(Chat.updated_at.desc())
    ).all()

    return {
        "totals": {
            "users": user_count,
            "chats": chat_count,
            "documents": document_count,
        },
        "users": [
            {
                "id": str(row.id),
                "email": row.email,
                "chats": row.chat_count,
                "documents": row.document_count,
            }
            for row in user_rows
        ],
        "chats": [
            {
                "id": str(row.id),
                "title": row.title,
                "user_id": str(row.user_id),
                "documents": row.document_count,
            }
            for row in chat_rows
        ],
        "viewer_id": str(current_user.id),
    }