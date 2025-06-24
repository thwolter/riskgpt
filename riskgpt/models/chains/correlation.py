"""
Correlation models for RiskGPT.

This module contains models for correlation analysis between risks.
"""

from typing import List, Optional

from pydantic import BaseModel

from riskgpt.models.base import BaseRequest
from riskgpt.models.chains.risk import Risk
from riskgpt.models.common import BusinessContext


class CorrelationTag(BaseModel):
    tag: str
    justification: str
    risk_ids: List[str]  # Use risk IDs or titles from the provided 'risks' input


class CorrelationTagRequest(BaseRequest):
    """Input model for defining correlation tags."""

    business_context: BusinessContext
    risks: List[Risk]
    known_drivers: Optional[List[str]] = None


class CorrelationTagResponse(BaseModel):
    """Output model containing correlation tags."""

    correlation_tags: List[CorrelationTag]
    rationale: Optional[str] = None
