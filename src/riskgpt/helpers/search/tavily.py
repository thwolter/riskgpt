"""Tavily search provider implementation."""

from typing import List

from langchain_tavily import TavilySearch

from riskgpt.config.settings import RiskGPTSettings
from riskgpt.helpers.circuit_breaker import tavily_breaker, with_fallback
from riskgpt.helpers.search.base import BaseSearchProvider
from riskgpt.helpers.search.utils import create_fallback_function
from riskgpt.logger import logger
from riskgpt.models.helpers.search import SearchRequest, SearchResponse, SearchResult

settings = RiskGPTSettings()


class TavilySearchProvider(BaseSearchProvider):
    """Tavily search provider implementation."""

    def __init__(self):
        """Initialize the Tavily search provider."""
        self.fallback = create_fallback_function(self)

    @tavily_breaker
    @with_fallback(lambda self, payload: self.fallback(payload))
    async def search(self, payload: SearchRequest) -> SearchResponse:
        """Perform a Tavily search and format results."""

        if payload.source_type.value.lower() in ["general", "news", "finance"]:
            topic = payload.source_type.value.lower()
            query = payload.query
        else:
            topic = "general"  # Default to general for unsupported types
            query = f"{payload.source_type.value} {payload.query}"

        results: List[SearchResult] = []

        if not settings.TAVILY_API_KEY:
            logger.warning("Tavily API key not configured")
            return SearchResponse(
                results=results,
                success=False,
                error_message="Tavily API key not configured",
            )

        try:
            tool = TavilySearch(
                tavily_api_key=settings.TAVILY_API_KEY.get_secret_value(),
                max_results=payload.max_results,
                topic=topic,
                include_answer="basic",
                include_raw_content="text",
            )

            # Note: TavilySearch.invoke is not async, but we're keeping
            # the method signature async to match the interface
            search_results = tool.invoke(query)

            # Check if we got valid results
            if not search_results:
                logger.warning("No valid search results returned")
                return SearchResponse(
                    results=results,
                    success=False,
                    error_message="No valid search results",
                )

            for item in search_results.get("results", []):
                results.append(
                    SearchResult(
                        title=item.get("title", ""),
                        url=item.get("url", ""),
                        date=item.get("published_date", ""),
                        type=payload.source_type.value,
                        content=item.get("raw_content", ""),
                        score=item.get("score", None),
                    )
                )

            return SearchResponse(
                results=results, success=bool(results), error_message=""
            )

        except Exception as exc:  # pragma: no cover - search failure should not crash
            logger.error("Tavily search failed: %s", exc)
            return self.format_error_response(f"Tavily search failed: {exc}")
