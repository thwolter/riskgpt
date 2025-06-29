from typing import List, Optional

from pydantic import Field

from riskgpt.models.base import BaseRequest, BaseResponse
from riskgpt.models.chains.risk import Risk
from riskgpt.models.enums import TopicEnum
from riskgpt.models.helpers import SearchRequest
from riskgpt.models.workflows.context import ResearchRequest


class RiskAnalysisRequest(BaseRequest):
    """Input model for risk analysis."""

    research_request: ResearchRequest
    risk: Risk = Field(description="The risk to analyze")

    @classmethod
    def from_risk(
        cls, risk: Risk, focus_keywords: Optional[List[str]] = None, **kwargs
    ) -> "RiskAnalysisRequest":
        """Create a RiskAnalysisRequest from a Risk."""
        research_request = ResearchRequest.from_risk(
            risk=risk, focus_keywords=focus_keywords, **kwargs
        )
        return cls(
            research_request=research_request,
            risk=risk,
        )

    def create_search_request(self, topic: TopicEnum) -> SearchRequest:
        """Create a search request for the specified topic."""
        return self.research_request.create_search_request(topic)


class RiskAnalysisResponse(BaseResponse):
    """Output model containing risk analysis information."""

    risk_summary: str
    risk_factors: List[str]
    mitigation_strategies: List[str]
    impact_assessment: str
    document_references: Optional[List[str]] = None
    full_report: Optional[str] = None
