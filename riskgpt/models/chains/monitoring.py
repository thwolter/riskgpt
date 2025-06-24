"""
Monitoring models for RiskGPT.

This module contains models for deriving monitoring indicators for risks.
"""

from typing import List, Optional

from pydantic import Field

from riskgpt.models.base import BaseRequest, BaseResponse
from riskgpt.models.common import BusinessContext


class MonitoringRequest(BaseRequest):
    """Input for deriving monitoring indicators."""

    business_context: BusinessContext = Field(
        description="Business context information"
    )
    risk_description: str = Field(
        description="Risk description to derive monitoring indicators for"
    )


class MonitoringResponse(BaseResponse):
    """Output model containing monitoring indicators."""

    indicators: List[str] = Field(
        description="List of identified monitoring indicators"
    )
    references: Optional[List[str]] = Field(
        default=None, description="References used for indicator identification"
    )
