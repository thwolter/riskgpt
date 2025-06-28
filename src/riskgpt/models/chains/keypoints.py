from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from riskgpt.models.base import BaseResponse
from riskgpt.models.enums import TopicEnum
from riskgpt.models.helpers import Source
from riskgpt.models.helpers.citation import Citation


class KeyPoint(BaseModel):
    """Model for a key point extracted from a source."""

    content: str
    topic: TopicEnum
    source_url: Optional[str] = None
    additional_sources: List[str] = []
    citation: Optional[Citation] = None
    additional_citations: List[Citation] = []

    def get_inline_citation(self) -> str:
        """Get Harvard-style inline citation."""
        if self.citation:
            return self.citation.format_harvard_citation()
        elif self.source_url:
            # Fallback to simple URL-based citation
            from urllib.parse import urlparse

            domain = urlparse(self.source_url).netloc
            return domain
        return ""


class ExtractKeyPointsRequest(BaseModel):
    """Input model for extracting key points from a source."""

    source_type: str
    content: str
    focus_keywords: Optional[List[str]] = []

    @classmethod
    def from_source(
        cls, source: Source, focus_keywords: Optional[List[str]] = None
    ) -> "ExtractKeyPointsRequest":
        """Create an ExtractKeyPointsRequest from a Source object."""
        return ExtractKeyPointsRequest(
            source_type=source.type,
            content=f"Title: {source.title}\n\nContent: {source.content}",
            focus_keywords=focus_keywords or [],
        )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "source_type": "NEWS",
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
                        "topic": "NEWS",
                        "source_url": "https://example.com",
                    },
                    {
                        "content": "Key point 2",
                        "topic": "NEWS",
                        "source_url": "https://example.com",
                    },
                    {
                        "content": "Key point 3",
                        "topic": "NEWS",
                        "source_url": "https://example.com",
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

    text: str
    references: List[str]

    def format_output(self) -> str:
        """Format the output text with references."""
        formatted_references = "\n".join(self.references)
        return f"{self.text}\n\nReferences:\n{formatted_references}"
