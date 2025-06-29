from typing import List, Optional

from pydantic import Field

from riskgpt.models.base import BaseRequest, BaseResponse
from riskgpt.models.chains.risk import Risk
from riskgpt.models.common import BusinessContext
from riskgpt.models.enums import TopicEnum
from riskgpt.models.helpers import SearchRequest


class ResearchRequest(BaseRequest):
    """Input model for external context enrichment."""

    query: str = Field(description="Search query string")
    focus_keywords: Optional[List[str]] = None
    time_horizon_months: Optional[int] = 12
    max_search_results: int = Field(default=3, ge=1, le=100)
    region: str = Field(
        default="wt-wt", description="Region for search results, default is worldwide"
    )

    @classmethod
    def from_business_context(
        cls,
        business_context: BusinessContext,
        focus_keywords: Optional[List[str]] = None,
        **kwargs,
    ) -> "ResearchRequest":
        """Create a ResearchRequest from a BusinessContext."""
        keywords = " ".join(focus_keywords) if focus_keywords else ""
        query = f"{business_context.project_description} {keywords}".strip()
        return cls(query=query, focus_keywords=focus_keywords, **kwargs)

    @classmethod
    def from_risk(
        cls, risk: Risk, focus_keywords: Optional[List[str]] = None, **kwargs
    ) -> "ResearchRequest":
        """Create a ResearchRequest from a Risk."""
        keywords = " ".join(focus_keywords) if focus_keywords else ""
        query = f"{risk.title} {risk.description} {keywords}".strip()
        return cls(query=query, focus_keywords=focus_keywords, **kwargs)

    def create_search_request(self, topic: TopicEnum) -> SearchRequest:
        """Create a search request for the specified topic."""
        return SearchRequest(
            query=self.query,
            source_type=topic,
            max_results=self.max_search_results,
            region=self.region,
        )


class ResearchResponse(BaseResponse):
    """Output model containing summarised external information."""

    summary: str
    recommendations: List[str]
    full_report: Optional[str] = None
