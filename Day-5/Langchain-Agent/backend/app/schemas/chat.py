from __future__ import annotations

from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ChatCreateRequest(BaseModel):
    title: str = Field(default="New conversation", min_length=1, max_length=200)


class ChatUpdateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)


class MessageCreateRequest(BaseModel):
    role: str = Field(pattern="^(user|assistant|system)$")
    content: str = Field(min_length=1, max_length=100000)


class AgentMessageRequest(BaseModel):
    content: str = Field(min_length=1, max_length=100000)


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    role: str
    content: str
    created_at: datetime


class ChatResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = []
