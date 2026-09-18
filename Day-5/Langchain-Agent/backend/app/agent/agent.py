from __future__ import annotations

from typing import Callable, List, Optional
from uuid import UUID

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.tools import BaseTool
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from sqlalchemy.orm import Session

from app.agent.prompts import build_agent_prompt
from app.core.config import get_settings
from app.rag.vectorstore import UserVectorStore, vector_store
from app.tools.document_tool import build_document_search_tool
from app.tools.search_tool import build_web_search_tool
from app.services.search_service import SearchResult


def build_agent_tools(
    db: Session,
    user_id: UUID,
    search: Optional[Callable[[str, int], List[SearchResult]]] = None,
    store: UserVectorStore = vector_store,
) -> List[BaseTool]:
    return [
        build_document_search_tool(db, user_id, store),
        build_web_search_tool(search),
    ]


def build_agent_executor(
    db: Session,
    user_id: UUID,
    llm=None,
    search: Optional[Callable[[str, int], List[SearchResult]]] = None,
    store: UserVectorStore = vector_store,
) -> AgentExecutor:
    settings = get_settings()
    if llm is not None:
        model = llm
    elif settings.llm_provider.lower() == "groq":
        model = ChatGroq(
            model=settings.llm_model,
            api_key=settings.groq_api_key,
            temperature=0,
        )
    else:
        model = ChatOpenAI(
            model=settings.llm_model,
            api_key=settings.llm_api_key,
            temperature=0,
        )
    tools = build_agent_tools(db, user_id, search, store)
    agent = create_tool_calling_agent(model, tools, build_agent_prompt())
    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=False,
        return_intermediate_steps=False,
        handle_parsing_errors=True,
    )
