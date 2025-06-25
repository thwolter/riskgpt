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
    external_risks: List[str]
    source_table: List[Dict[str, str]]
    workshop_recommendations: List[str]
    full_report: Optional[str] = None
    response_info: Optional[ResponseInfo] = None
