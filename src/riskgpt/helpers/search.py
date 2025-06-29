"""Search utilities for different search providers.

This module provides a unified interface for different search providers,
including DuckDuckGo, Google Custom Search API, and Wikipedia.
"""

from typing import List

from langchain_community.utilities import (
    DuckDuckGoSearchAPIWrapper,
    WikipediaAPIWrapper,
)
from langchain_google_community import GoogleSearchAPIWrapper
from langchain_tavily import TavilySearch

from riskgpt.config.settings import RiskGPTSettings
from riskgpt.helpers.circuit_breaker import (
    duckduckgo_breaker,
    google_search_breaker,
    tavily_breaker,
    wikipedia_breaker,
    with_fallback,
)
from riskgpt.logger import logger
from riskgpt.models.enums import TopicEnum
from riskgpt.models.utils.search import SearchRequest, SearchResponse, SearchResult

settings = RiskGPTSettings()


def _search_fallback(payload: SearchRequest) -> SearchResponse:
    """Fallback function when search is unavailable."""
    logger.warning("Circuit is open for search, using fallback")
    return SearchResponse(
        results=[], success=False, error_message="Search service is unavailable"
    )


@duckduckgo_breaker
@with_fallback(_search_fallback)
def _duckduckgo_search(payload: SearchRequest) -> SearchResponse:
    """Perform a DuckDuckGo search and format results."""

    results: List[SearchResult] = []
    try:
        wrapper = DuckDuckGoSearchAPIWrapper()
        search_results = wrapper.results(
            query=payload.query, max_results=payload.max_results
        )
        for item in search_results:
            results.append(
                SearchResult(
                    title=item.get("title", ""),
                    url=item.get("link", ""),
                    date=item.get("date") or "",
                    type=payload.source_type,
                    content=item.get("snippet", ""),
                )
            )
    except Exception as exc:  # pragma: no cover - search failure should not crash
        logger.error("DuckDuckGo search failed: %s", exc)
        return SearchResponse(
            results=results,
            success=False,
            error_message=f"DuckDuckGo search failed: {exc}",
        )
    return SearchResponse(results=results, success=bool(results), error_message="")


@google_search_breaker
@with_fallback(_search_fallback)
def _google_search(payload: SearchRequest) -> SearchResponse:
    """Perform a Google Custom Search and format results."""
    results: List[SearchResult] = []

    if not settings.GOOGLE_CSE_ID or not settings.GOOGLE_API_KEY:
        logger.warning("Google CSE ID or API key not configured")
        return SearchResponse(
            results=results,
            success=False,
            error_message="Google CSE ID or API key not configured",
        )

    try:
        api_key = settings.GOOGLE_API_KEY.get_secret_value()
        wrapper = GoogleSearchAPIWrapper(
            google_api_key=api_key,
            google_cse_id=settings.GOOGLE_CSE_ID,
        )

        search_results = wrapper.results(payload.query, num_results=payload.max_results)

        if not search_results or (
            len(search_results) == 1 and "Result" in search_results[0]
        ):
            logger.warning("No valid search results returned")
            return SearchResponse(
                results=results, success=False, error_message="No valid search results"
            )

        # Process the results
        for item in search_results:
            results.append(
                SearchResult(
                    title=item.get("title", ""),
                    url=item.get("link", ""),
                    date="",  # Google doesn't provide date in the same way
                    type=payload.source_type,
                    content=item.get("snippet", ""),
                )
            )

        # Return success only if we have results
        return SearchResponse(results=results, success=bool(results), error_message="")
    except Exception as exc:  # pragma: no cover - search failure should not crash
        logger.error("Google search failed: %s", exc)
        return SearchResponse(
            results=results, success=False, error_message=f"Google search failed: {exc}"
        )


@wikipedia_breaker
@with_fallback(_search_fallback)
def _wikipedia_search(payload: SearchRequest) -> SearchResponse:
    """Perform a Wikipedia search and format results."""

    results: List[SearchResult] = []

    try:
        wrapper = WikipediaAPIWrapper(
            wiki_client=None, top_k_results=payload.max_results
        )
        # Wikipedia API returns a single string with all results
        wiki_results = wrapper.load(payload.query)
        for item in wiki_results:
            results.append(
                SearchResult(
                    title=item.metadata.get("title", ""),
                    url=item.metadata.get("source", ""),
                    date="",  # Wikipedia doesn't provide date in the same way
                    type=payload.source_type,
                    content=item.metadata.get("summary", ""),
                )
            )
    except Exception as exc:  # pragma: no cover - search failure should not crash
        logger.error("Wikipedia search failed: %s", exc)
        return SearchResponse(
            results=results,
            success=False,
            error_message=f"Wikipedia search failed: {exc}",
        )
    return SearchResponse(results=results, success=bool(results), error_message="")


@tavily_breaker
@with_fallback(_search_fallback)
def _tavily_search(payload: SearchRequest) -> SearchResponse:
    """Perform a Tavily search and format results."""

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
            topic="news" if payload.source_type == TopicEnum.NEWS.value else "general",
            include_answer="basic",
            include_raw_content="text",
        )

        search_results = tool.invoke(payload.query)

        # Check if we got valid results
        if not search_results:
            logger.warning("No valid search results returned")
            return SearchResponse(
                results=results, success=False, error_message="No valid search results"
            )

        for item in search_results.get("results", []):
            results.append(
                SearchResult(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    date=item.get("published_date", ""),
                    type=payload.source_type,
                    content=item.get("raw_content", ""),
                    score=item.get("score", None),
                )
            )

        return SearchResponse(results=results, success=bool(results), error_message="")
    except Exception as exc:  # pragma: no cover - search failure should not crash
        logger.error("Tavily search failed: %s", exc)
        return SearchResponse(
            results=results,
            success=False,
            error_message=f"Tavily search failed: {exc}",
        )


def search(
    search_request: SearchRequest,
) -> SearchResponse:
    """Perform a search using the configured search provider."""

    # Perform primary search based on configured provider
    if settings.SEARCH_PROVIDER == "duckduckgo":
        primary_response = _duckduckgo_search(search_request)
    elif settings.SEARCH_PROVIDER == "google":
        primary_response = _google_search(search_request)
    elif settings.SEARCH_PROVIDER == "wikipedia":
        primary_response = _wikipedia_search(search_request)
    elif settings.SEARCH_PROVIDER == "tavily":
        primary_response = _tavily_search(search_request)
    else:
        # Default to empty response if provider is not recognized
        primary_response = SearchResponse(
            results=[],
            success=False,
            error_message=f"Unknown search provider: {settings.SEARCH_PROVIDER}",
        )

    # Additional Wikipedia search if enabled
    wiki_results: List[SearchResult] = []
    if settings.INCLUDE_WIKIPEDIA and settings.SEARCH_PROVIDER != "wikipedia":
        wiki_response = _wikipedia_search(search_request)
        wiki_results = wiki_response.results

    # Combine results
    all_results = primary_response.results + wiki_results
    return SearchResponse(
        results=all_results,
        success=primary_response.success or bool(wiki_results),
        error_message=primary_response.error_message
        if not primary_response.success and not wiki_results
        else "",
    )
