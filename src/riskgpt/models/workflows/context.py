from typing import List, Optional

from pydantic import Field

from riskgpt.models.base import BaseRequest, BaseResponse
from riskgpt.models.common import BusinessContext
from riskgpt.models.enums import TopicEnum
from riskgpt.models.helpers import SearchRequest


class EnrichContextRequest(BaseRequest):
    """Input model for external context enrichment."""

    business_context: BusinessContext
    focus_keywords: Optional[List[str]] = None
    time_horizon_months: Optional[int] = 12
    max_search_results: int = Field(default=3, ge=1, le=100)
    region: str = Field(
        default="wt-wt", description="Region for search results, default is worldwide"
    )

    def create_search_query(self) -> str:
        """Create a search query based on the business context and focus keywords."""
        keywords = " ".join(self.focus_keywords) if self.focus_keywords else ""
        return f"{self.business_context.project_description} {keywords}".strip()

    def create_search_request(self, topic: TopicEnum) -> SearchRequest:
        """Create a search request dictionary for the specified topic."""
        return SearchRequest(
            query=self.create_search_query(),
            source_type=topic,
            max_results=self.max_search_results,
            region=self.region,
        )


class EnrichContextResponse(BaseResponse):
    """Output model containing summarised external information."""

    sector_summary: str
    workshop_recommendations: List[str]
    full_report: Optional[str] = None
