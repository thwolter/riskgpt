"""Common utility functions for search providers."""

from typing import Any, Callable, Coroutine, List, TypeVar

from riskgpt.models.helpers.search import SearchRequest, SearchResponse, SearchResult

T = TypeVar("T")


def _search_fallback(payload: SearchRequest) -> SearchResponse:
    """Fallback function when search is unavailable."""
    return SearchResponse(
        results=[], success=False, error_message="Search service is unavailable"
    )


def create_fallback_function(
    provider_instance,
) -> Callable[[SearchRequest], Coroutine[Any, Any, SearchResponse]]:
    """Create a fallback function for a search provider.

    Args:
        provider_instance: The search provider instance

    Returns:
        A fallback function that can be used with the with_fallback decorator
    """

    async def fallback_function(payload):
        return provider_instance.format_error_response("Search service is unavailable")

    return fallback_function


def deduplicate_results(results: List[SearchResult]) -> List[SearchResult]:
    """Remove duplicate search results based on URL and content similarity.

    Args:
        results: List of search results to deduplicate

    Returns:
        Deduplicated list of search results
    """
    # First pass: Remove exact URL duplicates
    unique_urls: set[str] = set()
    unique_results: List[SearchResult] = []

    for result in results:
        # Normalize URL to handle slight variations
        normalized_url = result.url.rstrip("/").lower()
        if normalized_url not in unique_urls:
            unique_urls.add(normalized_url)
            unique_results.append(result)

    # Second pass: Check for content similarity (simple approach)
    final_results: List[SearchResult] = []
    for i, result in enumerate(unique_results):
        is_duplicate = False
        # Compare with results we've already decided to keep
        for kept_result in final_results:
            # Simple similarity check - if titles are very similar or content has high overlap
            if (
                result.title
                and kept_result.title
                and (
                    result.title.lower() in kept_result.title.lower()
                    or kept_result.title.lower() in result.title.lower()
                )
            ):
                # Check content similarity if both have content
                if result.content and kept_result.content:
                    # Simple overlap check - can be improved with more sophisticated methods
                    content_overlap = len(
                        set(result.content.lower().split())
                        & set(kept_result.content.lower().split())
                    )
                    total_words = len(
                        set(result.content.lower().split())
                        | set(kept_result.content.lower().split())
                    )
                    if (
                        total_words > 0 and content_overlap / total_words > 0.7
                    ):  # 70% similarity threshold
                        is_duplicate = True
                        break

        if not is_duplicate:
            final_results.append(result)

    return final_results


def rank_results(results: List[SearchResult]) -> List[SearchResult]:
    """Rank search results based on relevance and source reliability.

    Args:
        results: List of search results to rank

    Returns:
        Ranked list of search results
    """
    # Define source weights (can be adjusted based on preferences)
    source_weights: dict[str, float] = {
        "wikipedia": 0.8,  # Wikipedia is reliable but might not be the most relevant
        "news": 0.9,
        "regulatory": 1.0,  # Regulatory sources are highly trusted
        "professional": 0.9,
        "peer": 0.7,
        "": 0.5,  # Default for unspecified sources
    }

    # Calculate a score for each result
    for result in results:
        # Base score from the search provider (if available)
        score = result.score

        # Adjust score based on source type
        source_type = result.type.lower() if result.type else ""
        source_weight = source_weights.get(source_type, 0.5)

        # Identify Wikipedia results
        is_wikipedia = "wikipedia.org" in result.url.lower()

        # Apply source weighting
        if is_wikipedia:
            # Use Wikipedia-specific weight
            result.score = score * source_weights.get("wikipedia", 0.8)
        else:
            result.score = score * source_weight

    # Sort by score (descending)
    ranked_results: List[SearchResult] = sorted(
        results, key=lambda x: x.score, reverse=True
    )

    return ranked_results
