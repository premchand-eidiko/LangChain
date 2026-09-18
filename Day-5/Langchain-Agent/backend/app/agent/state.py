from __future__ import annotations

from typing import List

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from app.models import Message


def build_chat_history(messages: List[Message]) -> List[BaseMessage]:
    history = []
    for message in messages:
        if message.role == "user":
            history.append(HumanMessage(content=message.content))
        elif message.role == "assistant":
            history.append(AIMessage(content=message.content))
        elif message.role == "system":
            history.append(SystemMessage(content=message.content))
    return history