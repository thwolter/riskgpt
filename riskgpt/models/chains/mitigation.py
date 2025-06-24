"""
Mitigation models for RiskGPT.

This module contains models for risk mitigation measures.
"""

from typing import List, Optional

from pydantic import BaseModel, Field

from riskgpt.models.base import BaseRequest
from riskgpt.models.chains.drivers import RiskDriver
from riskgpt.models.chains.risk import Risk
from riskgpt.models.common import BusinessContext


class MitigationRequest(BaseRequest):
    """Input model for risk mitigation measures."""

    business_context: BusinessContext = Field(
        description="Business context information"
    )
    risk: Risk = Field(description="Risk information to identify mitigations for")
    risk_drivers: Optional[List[RiskDriver]] = Field(
        default=None,
        description="List of risk drivers to consider for mitigation identification",
    )


class Mitigation(BaseModel):
    driver: str = Field(
        description="Short description of the risk driver related to the mitigation"
    )
    mitigation: str = Field(description="Short description of the mitigation measure")
    explanation: str = Field(
        description="Detailed explanation of how the mitigation addresses the risk"
    )
    reference: Optional[str] = Field(
        default=None, description="Reference for the mitigation measure"
    )


class MitigationResponse(BaseModel):
    """Output model containing mitigation measures."""

    mitigations: List[Mitigation]


class CostBenefitRequest(BaseRequest):
    """Input for cost-benefit analysis of mitigations."""

    business_context: BusinessContext = Field(
        description="Business context information"
    )
    risk_title: str = Field(description="Title of the risk to analyze mitigations for")
    risk_description: str = Field(
        description="Risk description to analyze mitigations for"
    )
    mitigations: List[str] = Field(description="List of mitigation measures to analyze")


class CostBenefit(BaseModel):
    """Model for cost-benefit analysis of a single mitigation measure."""

    mitigation: str = Field(description="Mitigation measure being analyzed")
    cost: Optional[str] = Field(
        default=None, description="Cost estimate for the mitigation"
    )
    benefit: Optional[str] = Field(
        default=None, description="Benefit estimate for the mitigation"
    )


class CostBenefitResponse(BaseModel):
    """Output model containing cost-benefit analyses."""

    analyses: List[CostBenefit] = Field(
        description="List of cost-benefit analyses for mitigation measures"
    )
    references: Optional[List[str]] = Field(
        default=None, description="References used for the analyses"
    )
