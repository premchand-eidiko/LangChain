import httpx

from app.core.config import get_settings
from app.services.search_service import SearchResult, TavilySearchProvider
from app.tools.search_tool import WebSearchInput, build_web_search_tool


def test_tavily_provider_maps_results():
    def handler(request):
        assert request.url.path == "/search"
        assert request.method == "POST"
        return httpx.Response(
            200,
            json={
                "results": [
                    {
                        "title": "Python News",
                        "url": "https://example.com/python",
                        "content": "A current Python update.",
                    }
                ]
            },
        )

    provider = TavilySearchProvider(
        "test-key", client=httpx.Client(transport=httpx.MockTransport(handler))
    )
    results = provider.search("latest Python news")

    assert results[0].title == "Python News"
    assert results[0].url == "https://example.com/python"
    assert results[0].content == "A current Python update."


def test_web_search_tool_formats_injected_results():
    def fake_search(query, max_results):
        assert query == "latest Python news"
        assert max_results == 5
        return [SearchResult("Python News", "https://example.com", "Update")]

    tool = build_web_search_tool(fake_search)
    assert tool.args_schema is WebSearchInput
    output = tool.invoke({"query": "latest Python news"})

    assert "Python News" in output
    assert "https://example.com" in output
    assert "Update" in output


def test_web_search_tool_handles_missing_configuration(monkeypatch):
    monkeypatch.setenv("SEARCH_API_KEY", "")
    get_settings.cache_clear()
    try:
        tool = build_web_search_tool()
    finally:
        get_settings.cache_clear()

    assert tool.invoke({"query": "latest Python news"}) == (
        "Web search is not configured"
    )
