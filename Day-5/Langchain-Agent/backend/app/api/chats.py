from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing_extensions import Annotated

from app.api.dependencies import get_current_user
from app.database.session import get_db
from app.models import Chat, User
from app.schemas.chat import (
    ChatCreateRequest,
    ChatResponse,
    MessageCreateRequest,
    MessageResponse,
)
from app.services.chat_service import (
    add_message,
    create_chat,
    delete_user_chat,
    get_user_chat,
    list_user_chats,
)


router = APIRouter(prefix="/chats", tags=["chats"])


@router.post("", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
def create_new_chat(
    request: ChatCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Chat:
    return create_chat(db, current_user.id, request.title)


@router.get("", response_model=List[ChatResponse])
def list_chats(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> List[Chat]:
    return list_user_chats(db, current_user.id)


@router.get("/{chat_id}", response_model=ChatResponse)
def read_chat(
    chat_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Chat:
    chat = get_user_chat(db, current_user.id, chat_id)
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat


@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_chat(
    chat_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    if not delete_user_chat(db, current_user.id, chat_id):
        raise HTTPException(status_code=404, detail="Chat not found")


@router.post("/{chat_id}/messages", response_model=MessageResponse, status_code=201)
def create_chat_message(
    chat_id: UUID,
    request: MessageCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    message = add_message(
        db, current_user.id, chat_id, request.role, request.content
    )
    if message is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    return message
