from __future__ import annotations

import json
import logging
from typing import AsyncIterator
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing_extensions import Annotated

from app.agent.agent import build_agent_executor
from app.agent.state import build_chat_history
from app.api.dependencies import get_current_user
from app.core.observability import trace_chat_request
from app.database.session import get_db
from app.models import User
from app.schemas.chat import AgentMessageRequest
from app.services.chat_service import add_message, get_user_chat
from app.services.document_service import list_chat_documents
from app.tools.document_tool import build_document_search_tool


router = APIRouter(prefix="/chats", tags=["agent"])
logger = logging.getLogger(__name__)


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


def _is_document_question(text: str) -> bool:
    keywords = (
        "document", "doc", "paper", "author", "written by", "content",
        "chapter", "page", "pages", "slide", "slides", "section",
    )
    normalized = text.lower()
    return any(keyword in normalized for keyword in keywords)


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

    history = build_chat_history(chat.messages[-12:])
    chat_documents = list_chat_documents(db, current_user.id, chat_id)
    document_context = ""
    if chat_documents:
        filenames = ", ".join(document.filename for document in chat_documents)
        document_context = (
            "\n\nThe documents attached to this chat are: "
            + filenames
            + ". Use document_search for questions about them."
        )
    is_first_prompt = not any(message.role == "user" for message in chat.messages)
    user_message = add_message(db, current_user.id, chat_id, "user", request.content)
    if user_message is None:
        raise HTTPException(status_code=404, detail="Chat not found")

    if is_first_prompt:
        title = " ".join(request.content.split())
        chat.title = title[:57] + "..." if len(title) > 60 else title
        db.commit()

    try:
        executor = build_agent_executor(db, current_user.id, chat_id=chat_id)
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail="The AI service is not configured",
        ) from error

    async def generate() -> AsyncIterator[str]:
        answer_parts = []
        with trace_chat_request(current_user.id, chat_id, request.content) as (langfuse_handler, trace):
            invoke_config = {
                "metadata": {
                    "langfuse_user_id": str(current_user.id),
                    "langfuse_session_id": str(chat_id),
                    "langfuse_tags": ["chat", "document-aware"],
                }
            }
            if langfuse_handler is not None:
                invoke_config["callbacks"] = [langfuse_handler]
            try:
                async for event in executor.astream_events(
                    {"input": request.content + document_context, "chat_history": history},
                    config=invoke_config,
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
                        {"input": request.content + document_context, "chat_history": history},
                        config=invoke_config,
                    )
                    answer = str(result.get("output", "")).strip()
                    if answer:
                        yield _event({"type": "token", "content": answer})
                if answer:
                    add_message(db, current_user.id, chat_id, "assistant", answer)
                if trace is not None:
                    trace.update(output={"answer": answer}, metadata={"status": "success", "document_count": len(chat_documents)})
                yield _event({"type": "done"})
            except Exception as error:
                logger.exception("Agent response failed for chat %s", chat_id)
                error_text = str(error).lower()
                if "invalid api key" in error_text or "error code: 401" in error_text:
                    yield _event({"type": "error", "message": "Groq API key is invalid. Update GROQ_API_KEY in .env and restart the backend."})
                    return
                fallback = ""
                if chat_documents and _is_document_question(request.content):
                    try:
                        tool = build_document_search_tool(db, current_user.id, chat_id=chat_id)
                        document_id = str(chat_documents[0].id) if len(chat_documents) == 1 else None
                        fallback = tool.invoke({"query": request.content, "document_id": document_id})
                    except Exception:
                        fallback = ""
                if fallback:
                    add_message(db, current_user.id, chat_id, "assistant", fallback)
                    if trace is not None:
                        trace.update(output={"answer": fallback}, metadata={"status": "fallback", "document_count": len(chat_documents)})
                    yield _event({"type": "token", "content": fallback})
                    yield _event({"type": "done"})
                else:
                    if trace is not None:
                        trace.update(output={"status": "error"}, metadata={"error_type": type(error).__name__})
                    yield _event({"type": "error", "message": "The assistant could not complete this response"})

    return StreamingResponse(generate(), media_type="application/x-ndjson")