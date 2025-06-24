"""
Opportunity models for RiskGPT.

This module contains models for identifying opportunities from risks.
"""

from typing import List, Optional

from pydantic import BaseModel, Field

from src.models.base import BaseRequest
from src.models.chains.risk import Risk
from src.models.common import BusinessContext


class OpportunityRequest(BaseRequest):
    """Input for identifying opportunities."""

    business_context: BusinessContext = Field(
        description="Business context information"
    )
    risk: Risk = Field(description="Risk for which opportunities are to be identified")


class Opportunity(BaseModel):
    opportunity: str = Field(description="Description of the identified opportunity")
    explanation: str = Field(
        description="Explanation of how this opportunity relates to the risk"
    )
    category: Optional[str] = Field(
        default=None, description="Category of the opportunity, if applicable"
    )
    reference: Optional[str] = Field(
        default=None, description="Reference or source for the opportunity"
    )


class OpportunityResponse(BaseModel):
    """Output model containing identified opportunities."""

    opportunities: List[Opportunity]
