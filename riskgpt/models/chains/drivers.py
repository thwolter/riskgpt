"""
Driver models for RiskGPT.

This module contains models for risk driver identification.
"""

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from riskgpt.models.base import BaseResponse
from riskgpt.models.common import BusinessContext


class DriverRequest(BaseModel):
    """Input model for risk driver identification."""

    business_context: BusinessContext = Field(
        description="Business context information"
    )
    risk_description: str = Field(
        description="Risk description to identify drivers for"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "business_context": {
                    "project_id": "CRM-2023",
                    "project_description": "Implementation of a new CRM system",
                    "language": "en",
                },
                "risk_description": "There is a 30% probability that the CRM implementation will experience critical technical failures within the first 3 months of deployment.",
            }
        }
    )


class DriverResponse(BaseResponse):
    """Output model containing risk drivers."""

    drivers: List[str] = Field(description="List of identified risk drivers")
    references: Optional[List[str]] = Field(
        default=None, description="References used for driver identification"
    )

    @classmethod
    def model_validate(cls, obj, *args, **kwargs):
        # Handle case where references are lists of strings instead of strings
        if "references" in obj and isinstance(obj["references"], list):
            # Flatten any nested lists in references
            references = []
            for ref in obj["references"]:
                if isinstance(ref, list) and len(ref) > 0:
                    # Join the list into a single string or take the first element
                    references.append(ref[0])
                else:
                    references.append(ref)
            obj["references"] = references
        return super().model_validate(obj, *args, **kwargs)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "drivers": [
                    "Inadequate testing before deployment",
                    "Incompatibility with existing systems",
                    "Poor data quality in source systems",
                ],
                "references": [
                    "Industry report on CRM implementations",
                    "Internal lessons learned",
                ],
                "model_version": "1.0",
                "response_info": {
                    "consumed_tokens": 1300,
                    "total_cost": 0.026,
                    "prompt_name": "get_drivers",
                    "model_name": "gpt-4",
                },
            }
        }
    )
