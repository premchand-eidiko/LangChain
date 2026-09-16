from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from redis.exceptions import RedisError

from .chatbot import Chatbot
from .config import get_settings
from .memory import RedisMemory


settings = get_settings()
memory = RedisMemory(settings.redis_url, settings.memory_ttl_seconds)
chatbot = Chatbot(settings, memory)
app = FastAPI(title="AI Memory Chatbot")


class ChatRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=128)
    message: str = Field(min_length=1, max_length=10000)


class ChatResponse(BaseModel):
    session_id: str
    response: str


@app.get("/health")
def health() -> dict:
    try:
        memory.ping()
    except RedisError as error:
        raise HTTPException(status_code=503, detail="Redis is unavailable") from error
    return {"status": "ok", "redis": "connected"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    try:
        response = chatbot.reply(request.session_id, request.message)
    except RedisError as error:
        raise HTTPException(status_code=503, detail="Redis is unavailable") from error
    return ChatResponse(session_id=request.session_id, response=response)


@app.get("/memory/{session_id}")
def inspect_memory(session_id: str) -> dict:
    try:
        return {"session_id": session_id, "messages": memory.inspect(session_id)}
    except RedisError as error:
        raise HTTPException(status_code=503, detail="Redis is unavailable") from error


@app.delete("/memory/{session_id}")
def clear_memory(session_id: str) -> dict:
    try:
        cleared = memory.clear(session_id)
    except RedisError as error:
        raise HTTPException(status_code=503, detail="Redis is unavailable") from error
    return {"session_id": session_id, "cleared": cleared}
