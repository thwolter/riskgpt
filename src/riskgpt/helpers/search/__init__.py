"""Search utilities for different search providers.

This module provides a unified interface for different search providers,
including DuckDuckGo, Google Custom Search API, Wikipedia, and Tavily.
"""

import concurrent.futures
from typing import Optional

from riskgpt.config.settings import RiskGPTSettings
from riskgpt.helpers.search.base import BaseSearchProvider
from riskgpt.helpers.search.factory import get_search_provider
from riskgpt.helpers.search.utils import deduplicate_results, rank_results
from riskgpt.helpers.search.wikipedia import WikipediaSearchProvider
from riskgpt.logger import logger
from riskgpt.models.enums import TopicEnum
from riskgpt.models.helpers.search import SearchRequest, SearchResponse, SearchResult

settings = RiskGPTSettings()


def _should_include_wikipedia(request: SearchRequest) -> bool:
    """Determine if Wikipedia search should be included for this query.

    Wikipedia is most useful for:
    - General knowledge queries
    - Definitions and explanations
    - Historical information
    - Less useful for very recent events or specialized industry topics

    Args:
        request: The search request

    Returns:
        True if Wikipedia should be included, False otherwise
    """
    query = request.query.lower()

    # Keywords that suggest Wikipedia would be valuable
    knowledge_keywords = [
        "what is",
        "definition",
        "explain",
        "history",
        "background",
        "overview",
        "introduction to",
        "concept of",
        "theory",
        "principles",
        "fundamentals",
    ]

    # Check if query contains knowledge-seeking keywords
    for keyword in knowledge_keywords:
        if keyword in query:
            return True

    # For regulatory searches, Wikipedia often has good background information
    if request.source_type.value.lower() == "regulatory":
        return True

    # For news searches, Wikipedia might be less relevant for current events
    if request.source_type.value.lower() == "news":
        # Check for time-sensitive keywords
        time_keywords = [
            "latest",
            "recent",
            "today",
            "yesterday",
            "this week",
            "breaking",
        ]
        for keyword in time_keywords:
            if keyword in query:
                return False

    # Default to user setting
    return settings.INCLUDE_WIKIPEDIA


def _execute_search(provider, request: SearchRequest) -> SearchResponse:
    """Execute a search with a specific provider."""
    try:
        return provider.search(request)
    except Exception as e:
        logger.error(f"Error in search execution: {e}")
        return SearchResponse(results=[], success=False, error_message=str(e))


def search(
    search_request: SearchRequest, provider: Optional[BaseSearchProvider] = None
) -> SearchResponse:
    """Perform a search using the configured search provider with improvements."""

    # Get the primary search provider
    provider = provider or get_search_provider()

    # Prepare for parallel execution
    search_tasks = [(provider, search_request, provider.__class__.__name__)]

    # Add Wikipedia search if enabled and appropriate for this query
    # Exclude Wikipedia for academic searches
    include_wiki = (
        settings.INCLUDE_WIKIPEDIA
        and settings.SEARCH_PROVIDER != "wikipedia"
        and search_request.source_type != TopicEnum.ACADEMIC
        and (
            not settings.WIKIPEDIA_CONTEXT_AWARE
            or _should_include_wikipedia(search_request)
        )
    )

    if include_wiki:
        # Create a modified request with limited results for Wikipedia
        wiki_request = SearchRequest(
            query=search_request.query,
            source_type=search_request.source_type,
            max_results=min(search_request.max_results, settings.WIKIPEDIA_MAX_RESULTS),
            region=search_request.region,
        )
        wiki_provider = WikipediaSearchProvider()
        search_tasks.append((wiki_provider, wiki_request, "WikipediaSearchProvider"))

    # Execute searches in parallel
    all_results = []
    success = False
    error_message = ""

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=len(search_tasks)
    ) as executor:
        # Submit all search tasks
        future_to_provider = {
            executor.submit(_execute_search, provider, req): provider_name
            for provider, req, provider_name in search_tasks
        }

        # Process results as they complete
        for future in concurrent.futures.as_completed(future_to_provider):
            provider_name = future_to_provider[future]
            try:
                response = future.result()
                all_results.extend(response.results)
                if response.success:
                    success = True
                elif not success:  # Only keep error message if no success yet
                    error_message = response.error_message
            except Exception as exc:
                logger.error(
                    f"Search with {provider_name} generated an exception: {exc}"
                )

    # Deduplicate and rank results
    final_results = rank_results(deduplicate_results(all_results))

    return SearchResponse(
        results=final_results,
        success=success,
        error_message="" if success else error_message,
    )


# Re-export the search function and models for backward compatibility
__all__ = [
    "search",
    "SearchRequest",
    "SearchResponse",
    "SearchResult",
    "_should_include_wikipedia",
]
