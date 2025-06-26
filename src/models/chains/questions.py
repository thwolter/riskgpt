from typing import List, Optional

from pydantic import BaseModel, Field

from src.models.base import BaseResponse
from src.models.common import BusinessContext
from src.models.enums import AudienceEnum


class ChallengeQuestionsRequest(BaseModel):
    """Request model for generating challenging questions from business context."""

    business_context: BusinessContext
    audience: AudienceEnum = Field(
        description="The target audience for the questions",
        default=AudienceEnum.risk_internal,
    )
    focus_areas: Optional[List[str]] = Field(
        default=None,
        description="Specific areas to focus on when generating questions",
    )
    num_questions: int = Field(
        default=5,
        description="Number of challenging questions to generate",
        ge=1,
        le=10,
    )

    class Config:
        schema_extra = {
            "example": {
                "business_context": {
                    "project_id": "CRM-2023",
                    "project_description": "Implementation of a new CRM system",
                    "domain_knowledge": "The company operates in the B2B sector",
                    "business_area": "Sales",
                    "industry_sector": "Technology",
                },
                "audience": "risk_internal",
                "focus_areas": ["data security", "user adoption", "integration"],
                "num_questions": 5,
            }
        }


class ChallengeQuestionsResponse(BaseResponse):
    """Output model containing challenging questions derived from business context."""

    questions: List[str]

    class Config:
        schema_extra = {
            "example": {
                "questions": [
                    "What are the potential data security risks when migrating customer data to the new CRM system?",
                    "How might the implementation of the new CRM system affect existing sales processes?",
                    "What integration challenges might arise with existing systems?",
                    "What user adoption barriers might impact the success of the CRM implementation?",
                    "How might the new CRM system affect compliance with industry regulations?",
                ],
                "response_info": {"token_usage": 100, "cost": 0.01},
            }
        }
