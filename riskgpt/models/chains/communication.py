"""
Communication models for RiskGPT.

This module contains models for the communicate_risks chain.
"""

from typing import List, Optional

from pydantic import Field

from riskgpt.models.base import BaseRequest, BaseResponse
from riskgpt.models.chains.risk import Risk
from riskgpt.models.common import BusinessContext
from riskgpt.models.enums import AudienceEnum


class CommunicationRequest(BaseRequest):
    """Input for summarising risks for stakeholders."""

    business_context: BusinessContext
    audience: AudienceEnum = Field(
        default=AudienceEnum.executive,
        description="Target audience for the communication",
    )
    risks: List[Risk]


class CommunicationResponse(BaseResponse):
    """Output model for risk communication."""

    summary: str = Field(description="Audience-specific summary of risks")
    key_points: List[str] = Field(
        default_factory=list, description="Key points for communication"
    )
    technical_annex: Optional[str] = Field(
        default=None, description="Technical details for analysts"
    )
