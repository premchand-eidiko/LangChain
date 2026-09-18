from __future__ import annotations

from typing import Callable, List

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.services.search_service import (
    SearchProviderError,
    SearchResult,
    TavilySearchProvider,
    format_search_results,
)


class WebSearchInput(BaseModel):
    query: str = Field(
        min_length=1,
        max_length=2000,
        description="A current or general question to search on the web",
    )


def build_web_search_tool(
    search: Callable[[str, int], List[SearchResult]] | None = None,
) -> StructuredTool:
    settings = get_settings()
    provider = TavilySearchProvider(settings.search_api_key)
    search_function = search or provider.search

    def search_web(query: str) -> str:
        try:
            return format_search_results(search_function(query, 5))
        except SearchProviderError as error:
            return str(error)

    return StructuredTool.from_function(
        func=search_web,
        name="web_search",
        description=(
            "Search the public web for current information or facts that are "
            "not available in the user's uploaded documents."
        ),
        args_schema=WebSearchInput,
    )
