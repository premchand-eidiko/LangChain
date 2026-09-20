from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.chats import router as chats_router
from app.api.documents import router as documents_router
from app.api.agent_chat import router as agent_chat_router
from app.api.analytics import router as analytics_router
from app.core.config import get_settings
from app.core.observability import flush_langfuse
from app.database.init_db import create_tables


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    create_tables()
    try:
        yield
    finally:
        flush_langfuse()

app = FastAPI(
    title="Production Multi-Tool Conversational AI Agent",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in get_settings().cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(chats_router)
app.include_router(documents_router)
app.include_router(agent_chat_router)
app.include_router(analytics_router)


@app.get("/health")
def health_check() -> Dict[str, str]:
    return {"status": "ok"}
