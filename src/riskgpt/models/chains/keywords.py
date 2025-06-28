"""
Models for the extract_keywords chain.

This module contains the request and response models for the extract_keywords chain.
"""

from pydantic import Field

from riskgpt.models.base import BaseRequest, BaseResponse


class ExtractKeywordsRequest(BaseRequest):
    """Request model for extracting keywords from a query."""

    query: str = Field(description="The query text to extract keywords from")
    max_keywords: int = Field(
        default=5, description="Maximum number of keywords to extract"
    )


class ExtractKeywordsResponse(BaseResponse):
    """Response model for the extract_keywords chain."""

    keywords: str = Field(description="The extracted keywords separated by spaces")

    def format_output(self) -> str:
        """Format the response for output."""
        return self.keywords
