from __future__ import annotations

import json
from typing import AsyncIterator
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing_extensions import Annotated

from app.agent.agent import build_agent_executor
from app.agent.state import build_chat_history
from app.api.dependencies import get_current_user
from app.database.session import get_db
from app.models import User
from app.schemas.chat import AgentMessageRequest
from app.services.chat_service import add_message, get_user_chat


router = APIRouter(prefix="/chats", tags=["agent"])


def _event(payload: dict) -> str:
    return json.dumps(payload) + "\n"


def _content_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            item.get("text", "") for item in content if isinstance(item, dict)
        )
    return ""


@router.post("/{chat_id}/message")
async def send_agent_message(
    chat_id: UUID,
    request: AgentMessageRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> StreamingResponse:
    chat = get_user_chat(db, current_user.id, chat_id)
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")

    history = build_chat_history(chat.messages)
    user_message = add_message(db, current_user.id, chat_id, "user", request.content)
    if user_message is None:
        raise HTTPException(status_code=404, detail="Chat not found")

    try:
        executor = build_agent_executor(db, current_user.id)
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail="The AI service is not configured",
        ) from error

    async def generate() -> AsyncIterator[str]:
        answer_parts = []
        try:
            async for event in executor.astream_events(
                {"input": request.content, "chat_history": history},
                version="v1",
            ):
                if event.get("event") != "on_chat_model_stream":
                    continue
                text = _content_text(event.get("data", {}).get("chunk").content)
                if text:
                    answer_parts.append(text)
                    yield _event({"type": "token", "content": text})

            answer = "".join(answer_parts).strip()
            if not answer:
                result = await executor.ainvoke(
                    {"input": request.content, "chat_history": history}
                )
                answer = str(result.get("output", "")).strip()
                if answer:
                    yield _event({"type": "token", "content": answer})
            if answer:
                add_message(db, current_user.id, chat_id, "assistant", answer)
            yield _event({"type": "done"})
        except Exception as error:
            error_text = str(error).lower()
            if "invalid api key" in error_text or "error code: 401" in error_text:
                message = "Groq API key is invalid. Update GROQ_API_KEY in .env and restart the backend."
            else:
                message = "The assistant could not complete this response"
            yield _event(
                {
                    "type": "error",
                    "message": message,
                }
            )

    return StreamingResponse(generate(), media_type="application/x-ndjson")