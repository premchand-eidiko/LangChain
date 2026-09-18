from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import httpx


@dataclass
class SearchResult:
    title: str
    url: str
    content: str


class SearchProviderError(Exception):
    pass


class TavilySearchProvider:
    endpoint = "https://api.tavily.com/search"

    def __init__(
        self,
        api_key: str,
        client: Optional[httpx.Client] = None,
    ) -> None:
        self.api_key = api_key
        self.client = client or httpx.Client(timeout=15.0)

    def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        if not self.api_key:
            raise SearchProviderError("Web search is not configured")
        if not query.strip():
            raise SearchProviderError("A search query is required")

        try:
            response = self.client.post(
                self.endpoint,
                json={
                    "api_key": self.api_key,
                    "query": query,
                    "max_results": max_results,
                    "search_depth": "basic",
                },
            )
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError) as error:
            raise SearchProviderError("Web search is temporarily unavailable") from error

        results = []
        for item in payload.get("results", []):
            if not isinstance(item, dict):
                continue
            results.append(
                SearchResult(
                    title=str(item.get("title", "Untitled result")),
                    url=str(item.get("url", "")),
                    content=str(item.get("content", "")),
                )
            )
        return results


def format_search_results(results: List[SearchResult]) -> str:
    if not results:
        return "No web search results were found."
    sections = []
    for index, result in enumerate(results, start=1):
        sections.append(
            "[Result {}] {}\nURL: {}\n{}".format(
                index, result.title, result.url, result.content
            )
        )
    return "\n\n".join(sections)
