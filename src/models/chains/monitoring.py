"""
Monitoring models for RiskGPT.

This module contains models for deriving monitoring indicators for risks.
"""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from src.models.base import BaseRequest
from src.models.chains.risk import Risk
from src.models.common import BusinessContext


class MonitoringRequest(BaseRequest):
    """Input for deriving monitoring indicators."""

    business_context: BusinessContext = Field(
        description="Business context information"
    )
    risk: Risk = Field(
        description="Risk information for which monitoring indicators are derived"
    )


class RiskIndicator(BaseModel):
    indicator: str = Field(description="Name of the monitoring indicator")
    type: Literal["leading", "lagging", "both"] = Field(
        description="Type of the indicator, whether it is leading, lagging, or both"
    )
    explanation: str = Field(
        description="Explanation of the indicator and its relevance to the risk"
    )
    action: Optional[str] = Field(
        default=None, description="Recommended action based on the indicator"
    )
    reference: Optional[str] = Field(
        default=None, description="Reference for the indicator, if applicable"
    )


class MonitoringResponse(BaseModel):
    """Output model containing monitoring indicators."""

    indicators: List[RiskIndicator]
