"""
Bias check models for RiskGPT.

This module contains models for checking biases in risk descriptions.
"""

from typing import List, Optional

from pydantic import BaseModel

from src.models.base import BaseResponse
from src.models.common import BusinessContext


class BiasCheckRequest(BaseModel):
    """Input for checking risk description biases."""

    business_context: Optional[BusinessContext] = None
    risk_description: str


class BiasCheckResponse(BaseResponse):
    """Output model containing identified biases and suggestions."""

    biases: List[str]
    suggestions: Optional[str] = None
