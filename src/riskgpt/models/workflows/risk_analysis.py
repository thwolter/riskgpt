from typing import List, Optional

from pydantic import Field

from riskgpt.models.base import BaseResponse
from riskgpt.models.chains.risk import Risk
from riskgpt.models.enums import TopicEnum
from riskgpt.models.helpers import SearchRequest
from riskgpt.models.workflows.context import EnrichContextRequest


class RiskAnalysisRequest(EnrichContextRequest):
    """Input model for risk analysis that extends EnrichContextRequest."""

    risk: Risk = Field(description="The risk to analyze")

    def create_search_query(self) -> str:
        """Create a search query focused on the risk."""
        keywords = " ".join(self.focus_keywords) if self.focus_keywords else ""
        return f"{self.risk.title} {self.risk.description} {keywords}".strip()

    def create_search_request(self, topic: TopicEnum) -> SearchRequest:
        """Create a search request dictionary for the specified topic."""
        return SearchRequest(
            query=self.create_search_query(),
            source_type=topic,
            max_results=self.max_search_results,
            region=self.region,
        )


class RiskAnalysisResponse(BaseResponse):
    """Output model containing risk analysis information."""

    risk_summary: str
    risk_factors: List[str]
    mitigation_strategies: List[str]
    impact_assessment: str
    document_references: Optional[List[str]] = None
    full_report: Optional[str] = None
