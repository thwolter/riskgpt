from typing import Dict, List, Optional

from pydantic import BaseModel

from src.models.base import BaseResponse, ResponseInfo
from src.models.common import BusinessContext


class ExternalContextRequest(BaseModel):
    """Input model for external context enrichment."""

    business_context: BusinessContext
    focus_keywords: Optional[List[str]] = None
    time_horizon_months: Optional[int] = 12


class ExternalContextResponse(BaseResponse):
    """Output model containing summarised external information."""

    sector_summary: str
    key_points: List[str]
    source_table: List[Dict[str, str]]
    workshop_recommendations: List[str]
    full_report: Optional[str] = None
    response_info: Optional[ResponseInfo] = None


class ExtractKeyPointsResponse(BaseResponse):
    """Model for key points extracted from a source."""

    points: List[str] = []

    class Config:
        schema_extra = {
            "example": {
                "points": ["Key point 1", "Key point 2", "Key point 3"],
                "response_info": {"token_usage": 100, "cost": 0.01},
            }
        }
