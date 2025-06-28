"""Common utility functions for search providers."""

from typing import Callable, TypeVar

from riskgpt.models.helpers.search import SearchRequest, SearchResponse

T = TypeVar("T")


def _search_fallback(payload: SearchRequest) -> SearchResponse:
    """Fallback function when search is unavailable."""
    return SearchResponse(
        results=[], success=False, error_message="Search service is unavailable"
    )


def create_fallback_function(
    provider_instance,
) -> Callable[[SearchRequest], SearchResponse]:
    """Create a fallback function for a search provider.

    Args:
        provider_instance: The search provider instance

    Returns:
        A fallback function that can be used with the with_fallback decorator
    """
    return lambda payload: provider_instance.format_error_response(
        "Search service is unavailable"
    )
