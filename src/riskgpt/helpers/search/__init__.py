"""Search utilities for different search providers.

This module provides a unified interface for different search providers,
including DuckDuckGo, Google Custom Search API, Wikipedia, and Tavily.
"""

from typing import List

from riskgpt.config.settings import RiskGPTSettings
from riskgpt.helpers.search.factory import get_search_provider
from riskgpt.helpers.search.wikipedia import WikipediaSearchProvider
from riskgpt.models.helpers.search import SearchRequest, SearchResponse, SearchResult

settings = RiskGPTSettings()


def search(search_request: SearchRequest) -> SearchResponse:
    """Perform a search using the configured search provider."""

    # Get the primary search provider
    provider = get_search_provider()
    primary_response = provider.search(search_request)

    # Additional Wikipedia search if enabled
    wiki_results: List[SearchResult] = []
    if settings.INCLUDE_WIKIPEDIA and settings.SEARCH_PROVIDER != "wikipedia":
        wiki_provider = WikipediaSearchProvider()
        wiki_response = wiki_provider.search(search_request)
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


# Re-export the search function and models for backward compatibility
__all__ = ["search", "SearchRequest", "SearchResponse", "SearchResult"]
