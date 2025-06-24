"""
Correlation models for RiskGPT.

This module contains models for correlation analysis between risks.
"""

from typing import List, Optional

from pydantic import BaseModel

from riskgpt.models.base import BaseResponse
from riskgpt.models.common import BusinessContext


class CorrelationTagRequest(BaseModel):
    """Input model for defining correlation tags."""

    business_context: BusinessContext
    risk_titles: List[str]
    known_drivers: Optional[List[str]] = None


class CorrelationTagResponse(BaseResponse):
    """Output model containing correlation tags."""

    tags: List[str]
    rationale: Optional[str] = None
