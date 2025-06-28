"""Base class for all search providers."""

from abc import ABC, abstractmethod

from riskgpt.models.helpers.search import SearchRequest, SearchResponse


class BaseSearchProvider(ABC):
    """Base class for all search providers."""

    @abstractmethod
    async def search(self, request: SearchRequest) -> SearchResponse:
        """Perform a search using this provider."""
        pass

    def format_error_response(self, error_message: str) -> SearchResponse:
        """Create an error response."""
        return SearchResponse(results=[], success=False, error_message=error_message)
