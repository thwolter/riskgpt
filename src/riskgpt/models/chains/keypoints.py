from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from riskgpt.models.base import BaseResponse
from riskgpt.models.enums import ScopeEnum
from riskgpt.models.helpers import Source
from riskgpt.models.helpers.citation import Citation


class KeyPoint(BaseModel):
    """Model for a key point extracted from a source."""

    content: str
    scope: ScopeEnum = Field(
        description="Type of the source, e.g., NEWS, RESEARCH, etc.",
        default=ScopeEnum.NEWS,
    )
    additional_sources: List[str] = []
    citation: Citation = Field(
        description="Citation information for the key point, including author, title, and publication details",
    )
    additional_citations: List[Citation] = []

    def get_inline_citation(self) -> str:
        """Get Harvard-style inline citation."""
        return self.citation.format_harvard_citation()


class ExtractKeyPointsRequest(BaseModel):
    """Input model for extracting key points from a source."""

    scope: ScopeEnum = Field(
        default=ScopeEnum.NEWS,
        description="Type of source to extract key points from, e.g., NEWS, RESEARCH, etc.",
    )
    content: str
    focus_keywords: Optional[List[str]] = []
    citation: Citation = Field(
        description="Citation information for the source, including author, title, and publication details",
    )

    @classmethod
    def from_source(
        cls, source: Source, focus_keywords: Optional[List[str]] = None
    ) -> "ExtractKeyPointsRequest":
        """Create an ExtractKeyPointsRequest from a Source object."""
        return ExtractKeyPointsRequest(
            scope=source.scope,
            content=f"{source.citation.title}\n\n{source.content}",
            focus_keywords=focus_keywords or [],
            citation=source.citation,
        )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "scope": "NEWS",
                "content": "This is an example content from a news article.",
            }
        }
    )


class ExtractKeyPointsResponse(BaseResponse):
    """Model for key points extracted from a source."""

    points: List[KeyPoint] = []

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "points": [
                    {
                        "content": "Key point 1",
                        "scope": "NEWS",
                        "citation": {
                            "url": "https://example.com/xyz",
                            "title": "Example Title",
                        },
                    },
                    {
                        "content": "Key point 2",
                        "scope": "NEWS",
                        "citation": {
                            "url": "https://example.com/xyz",
                            "title": "Example Title",
                        },
                    },
                ],
                "response_info": {
                    "consumed_tokens": 1400,
                    "total_cost": 0.028,
                    "prompt_name": "risk_assessment",
                    "model_name": "gpt-4",
                },
            }
        }
    )


class KeyPointSummaryRequest(BaseModel):
    """Request model for generating text from key points."""

    key_points: List[KeyPoint]


class KeyPointSummaryResponse(BaseResponse):
    """Output model containing text generated from key points with Harvard-style citations."""

    text: Optional[str] = Field(
        default=None,
        description="Generated text that incorporates all key points with inline citations.",
    )
    references: List[str] = Field(
        default_factory=list,
        description="List of references formatted in Harvard style.",
    )

    def format_output(self) -> str:
        """Format the output text with references."""
        formatted_references = "\n".join(self.references)
        return f"{self.text}\n\nReferences:\n{formatted_references}"
