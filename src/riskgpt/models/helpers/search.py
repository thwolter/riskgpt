from pydantic import BaseModel, Field

from riskgpt.models.enums import ScopeEnum
from riskgpt.models.helpers.citation import Citation


class SearchResult(BaseModel):
    scope: ScopeEnum = Field(
        default=ScopeEnum.NEWS,
        description="Type of source, e.g., news, professional, regulatory, peer",
    )
    content: str = Field(
        default="", description="Brief content or snippet from the source"
    )
    score: float = Field(
        default=0.0, description="Relevance score of the search result, if applicable"
    )
    citation: Citation = Field(
        description="Citation information for the source, including author, title, and publication details",
    )


class Source(SearchResult):
    """Source class that extends SearchResult with scope information."""

    scope: ScopeEnum = Field(
        default=ScopeEnum.NEWS,
        description="Type of source, e.g., news, professional, regulatory, peer",
    )

    @classmethod
    def from_search_result(
        cls, search_result: SearchResult, scope: ScopeEnum
    ) -> "Source":
        """Create a Source from a SearchResult and a scope."""
        return cls(
            content=search_result.content,
            citation=search_result.citation,
            scope=scope,
        )


class SearchRequest(BaseModel):
    """Request model for search queries."""

    query: str = Field(description="Search query string")
    scope: ScopeEnum = Field(
        default=ScopeEnum.NEWS,
        description="Type of source to search (e.g., news, professional, regulatory, peer)",
    )
    max_results: int = Field(
        default=3, ge=1, le=100, description="Maximum number of results to return"
    )
    region: str = "wt-wt"  # Default to 'wt-wt' for worldwide

    model_config = {
        "json_schema_extra": {
            "example": {
                "query": "latest developments in AI regulation",
                "scope": "news",
            }
        }
    }


class SearchResponse(BaseModel):
    """Response model for search results."""

    results: list[SearchResult] = Field(
        default_factory=list, description="List of search results"
    )
    success: bool = Field(
        default=True, description="Indicates if the search was successful"
    )
    error_message: str = Field(
        default="", description="Error message if the search failed"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "results": [
                    {
                        "title": "Example Title",
                        "url": "https://example.com",
                        "date": "2023-10-01",
                        "type": "news",
                        "content": "This is an example content.",
                    }
                ],
                "success": True,
                "error_message": "",
            }
        }
    }
