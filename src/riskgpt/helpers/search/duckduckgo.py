"""DuckDuckGo search provider implementation."""

from typing import List

from langchain_community.utilities import DuckDuckGoSearchAPIWrapper

from riskgpt.helpers.circuit_breaker import duckduckgo_breaker, with_fallback
from riskgpt.helpers.search.base import BaseSearchProvider
from riskgpt.helpers.search.utils import create_fallback_function
from riskgpt.logger import logger
from riskgpt.models.helpers.search import SearchRequest, SearchResponse, SearchResult


class DuckDuckGoSearchProvider(BaseSearchProvider):
    """DuckDuckGo search provider implementation."""

    def __init__(self):
        """Initialize the DuckDuckGo search provider."""
        self.fallback = create_fallback_function(self)

    @duckduckgo_breaker
    @with_fallback(lambda self, payload: self.fallback(payload))
    async def search(self, payload: SearchRequest) -> SearchResponse:
        """Perform a DuckDuckGo search and format results."""

        if payload.source_type.value.lower() in ["news"]:
            source_type = payload.source_type.value.lower()
            query = payload.query
        else:
            source_type = "text"  # Default to text for unsupported types
            query = f"{payload.source_type.value} {payload.query}"

        results: List[SearchResult] = []
        try:
            wrapper = DuckDuckGoSearchAPIWrapper(
                max_results=payload.max_results,
                region=payload.region,
                source=source_type,
            )
            # Note: DuckDuckGoSearchAPIWrapper.results is not async, but we're keeping
            # the method signature async to match the interface
            search_results = wrapper.results(
                query=query, max_results=payload.max_results
            )
            for item in search_results:
                results.append(
                    SearchResult(
                        title=item.get("title", ""),
                        url=item.get("link", ""),
                        date=item.get("date") or "",
                        type=payload.source_type.value,
                        content=item.get("snippet", ""),
                    )
                )

            return SearchResponse(
                results=results, success=bool(results), error_message=""
            )

        except Exception as exc:  # pragma: no cover - search failure should not crash
            logger.error("DuckDuckGo search failed: %s", exc)
            return self.format_error_response(f"DuckDuckGo search failed: {exc}")
