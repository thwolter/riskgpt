"""
Opportunity models for RiskGPT.

This module contains models for identifying opportunities from risks.
"""

from typing import List, Optional

from pydantic import Field

from riskgpt.models.base import BaseRequest, BaseResponse
from riskgpt.models.common import BusinessContext


class OpportunityRequest(BaseRequest):
    """Input for identifying opportunities."""

    business_context: BusinessContext = Field(
        description="Business context information"
    )
    risks: List[str] = Field(
        description="List of risk descriptions to identify opportunities from"
    )


class OpportunityResponse(BaseResponse):
    """Output model containing identified opportunities."""

    opportunities: List[str] = Field(description="List of identified opportunities")
    references: Optional[List[str]] = Field(
        default=None, description="References used for opportunity identification"
    )
