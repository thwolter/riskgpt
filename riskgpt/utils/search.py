"""Search utilities for different search providers.

This module provides a unified interface for different search providers,
including DuckDuckGo, Google Custom Search API, and Wikipedia.
"""

from typing import Any, Dict, List, Tuple

from riskgpt.config.settings import RiskGPTSettings
from riskgpt.logger import logger
from riskgpt.utils.circuit_breaker import (
    duckduckgo_breaker,
    google_search_breaker,
    wikipedia_breaker,
    with_fallback,
)

# Import search providers if available
DuckDuckGoSearchAPIWrapper: Any = None
GoogleSearchAPIWrapper: Any = None
WikipediaAPIWrapper: Any = None

try:
    from langchain_community.utilities import (
        DuckDuckGoSearchAPIWrapper as _DuckDuckGoWrapper,
    )

    DuckDuckGoSearchAPIWrapper = _DuckDuckGoWrapper
except ImportError:  # pragma: no cover - optional dependency
    logger.warning("duckduckgo-search not available")

try:
    from langchain_google_community import GoogleSearchAPIWrapper as _GoogleWrapper

    GoogleSearchAPIWrapper = _GoogleWrapper
except ImportError:  # pragma: no cover - optional dependency
    logger.warning("langchain-google-community not available")

try:

    # try to import the wrapper
    try:
        from langchain_community.utilities import (
            WikipediaAPIWrapper as _WikipediaWrapper,
        )

        WikipediaAPIWrapper = _WikipediaWrapper
    except ImportError:  # pragma: no cover - optional dependency
        logger.warning(
            "langchain_community.utilities.WikipediaAPIWrapper not available"
        )
        WikipediaAPIWrapper = None
except ImportError:  # pragma: no cover - optional dependency
    logger.warning(
        "wikipedia package not available, please install with 'pip install wikipedia'"
    )
    WikipediaAPIWrapper = None


def _search_fallback(query: str, source_type: str) -> Tuple[List[Dict[str, str]], bool]:
    """Fallback function when search is unavailable."""
    logger.warning("Circuit is open for search, using fallback")
    return [], False


@duckduckgo_breaker
@with_fallback(_search_fallback)
def _duckduckgo_search(
    query: str, source_type: str
) -> Tuple[List[Dict[str, str]], bool]:
    """Perform a DuckDuckGo search and format results."""
    results: List[Dict[str, str]] = []
    if DuckDuckGoSearchAPIWrapper is None:
        logger.warning("duckduckgo-search not available")
        return results, False
    try:
        wrapper = DuckDuckGoSearchAPIWrapper()
        for item in wrapper.results(query, max_results=3):
            results.append(
                {
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "date": item.get("date") or "",
                    "type": source_type,
                    "comment": item.get("snippet", ""),
                }
            )
    except Exception as exc:  # pragma: no cover - search failure should not crash
        logger.error("DuckDuckGo search failed: %s", exc)
        return results, False
    return results, True


@google_search_breaker
@with_fallback(_search_fallback)
def _google_search(query: str, source_type: str) -> Tuple[List[Dict[str, str]], bool]:
    """Perform a Google Custom Search and format results."""
    results: List[Dict[str, str]] = []
    if GoogleSearchAPIWrapper is None:
        logger.warning("langchain-google-community not available")
        return results, False

    settings = RiskGPTSettings()
    if not settings.GOOGLE_CSE_ID or not settings.GOOGLE_API_KEY:
        logger.warning("Google CSE ID or API key not configured")
        return results, False

    try:
        # Extract the API key from SecretStr
        api_key = (
            settings.GOOGLE_API_KEY.get_secret_value()
            if settings.GOOGLE_API_KEY
            else None
        )

        # Create the wrapper with the extracted API key
        wrapper = GoogleSearchAPIWrapper(
            google_api_key=api_key,
            google_cse_id=settings.GOOGLE_CSE_ID,
        )

        # Get search results
        search_results = wrapper.results(query, num_results=3)

        # Check if we got valid results
        if not search_results or (
            len(search_results) == 1 and "Result" in search_results[0]
        ):
            logger.warning("No valid search results returned")
            return results, False

        # Process the results
        for item in search_results:
            results.append(
                {
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "date": "",  # Google doesn't provide date in the same way
                    "type": source_type,
                    "comment": item.get("snippet", ""),
                }
            )

        # Return success only if we have results
        return results, bool(results)
    except Exception as exc:  # pragma: no cover - search failure should not crash
        logger.error("Google search failed: %s", exc)
        return results, False


@wikipedia_breaker
@with_fallback(_search_fallback)
def _wikipedia_search(
    query: str, source_type: str
) -> Tuple[List[Dict[str, str]], bool]:
    """Perform a Wikipedia search and format results."""
    results: List[Dict[str, str]] = []
    if WikipediaAPIWrapper is None:
        logger.warning("wikipedia not available")
        return results, False

    try:
        wrapper = WikipediaAPIWrapper(top_k_results=3)
        # Wikipedia API returns a single string with all results
        wiki_results = wrapper.run(query)
        if wiki_results:
            # Create a single result with the Wikipedia content
            results.append(
                {
                    "title": f"Wikipedia: {query}",
                    "url": f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}",
                    "date": "",
                    "type": source_type,
                    "comment": (
                        wiki_results[:500] + "..."
                        if len(wiki_results) > 500
                        else wiki_results
                    ),
                }
            )
    except Exception as exc:  # pragma: no cover - search failure should not crash
        logger.error("Wikipedia search failed: %s", exc)
        return results, False
    return results, True


def search(query: str, source_type: str) -> Tuple[List[Dict[str, str]], bool]:
    """Perform a search using the configured search provider.

    Args:
        query: The search query
        source_type: The type of source to search (e.g., "news", "social")

    Returns:
        A tuple containing a list of search results and a boolean indicating success
    """
    settings = RiskGPTSettings()

    # Primary search
    primary_results: List[Dict[str, str]] = []
    primary_success = False

    if settings.SEARCH_PROVIDER == "duckduckgo":
        primary_results, primary_success = _duckduckgo_search(query, source_type)
    elif settings.SEARCH_PROVIDER == "google":
        primary_results, primary_success = _google_search(query, source_type)
    elif settings.SEARCH_PROVIDER == "wikipedia":
        primary_results, primary_success = _wikipedia_search(query, source_type)

    # Additional Wikipedia search if enabled
    wiki_results: List[Dict[str, str]] = []
    if settings.INCLUDE_WIKIPEDIA and settings.SEARCH_PROVIDER != "wikipedia":
        wiki_results, _ = _wikipedia_search(query, source_type)

    # Combine results
    all_results = primary_results + wiki_results

    return all_results, primary_success or bool(wiki_results)
