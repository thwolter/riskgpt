from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Prompt(BaseModel):
    version: str
    description: str
    template: str


class LanguageEnum(str, Enum):
    """Supported languages for responses."""

    english = "en"
    german = "de"
    french = "fr"
    spanish = "es"
    italian = "it"
    portuguese = "pt"
    dutch = "nl"
    swedish = "sv"
    norwegian = "no"
    danish = "da"
    finnish = "fi"
    polish = "pl"
    russian = "ru"
    japanese = "ja"
    chinese = "zh"
    korean = "ko"


class ResponseInfo(BaseModel):
    consumed_tokens: int
    total_cost: float
    prompt_name: str
    model_name: str
    error: Optional[str] = None


class BaseResponse(BaseModel):
    """Base class for all response models."""

    model_version: str = Field(
        default="1.0", description="Schema version for backward compatibility"
    )
    response_info: Optional[ResponseInfo] = Field(
        default=None, description="Information about the response processing"
    )


class BusinessContext(BaseModel):
    """Standardized schema for business context information."""

    model_version: str = Field(
        default="1.0", description="Schema version for backward compatibility"
    )
    project_id: str = Field(
        description="Unique identifier for the project",
        examples=["PRJ-2023-001", "CRM-ROLLOUT-Q1"],
    )
    project_description: Optional[str] = Field(
        default=None,
        description="Detailed description of the project",
        examples=[
            "Implementation of a new CRM system",
            "Migration to cloud infrastructure",
        ],
    )
    domain_knowledge: Optional[str] = Field(
        default=None,
        description="Specific domain knowledge relevant to the project",
        examples=[
            "The company operates in the B2B sector",
            "Previous attempts at similar projects failed due to...",
        ],
    )
    business_area: Optional[str] = Field(
        default=None,
        description="Business area or department the project belongs to",
        examples=["Sales", "Marketing", "IT", "Finance"],
    )
    industry_sector: Optional[str] = Field(
        default=None,
        description="Industry sector the project operates in",
        examples=["Healthcare", "Finance", "Manufacturing", "Retail"],
    )
    language: Optional[LanguageEnum] = Field(
        default=LanguageEnum.english, description="Language for the response"
    )

    def get_domain_section(self) -> str:
        """Return formatted domain knowledge section if available."""
        return (
            f"Domain knowledge: {self.domain_knowledge}"
            if self.domain_knowledge
            else ""
        )


class Dist(BaseModel):
    """Generic distribution model."""

    name: str = Field(description="Name of the distribution")
    parameters: Optional[Dict[str, float]] = Field(
        default=None, description="Parameters of the distribution"
    )
    source: Optional[str] = Field(
        default=None, description="Source of the distribution"
    )
    correlation_tag: Optional[str] = Field(
        default=None, description="Tag for correlation analysis"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "normal",
                "parameters": {"mean": 100.0, "std": 10.0},
                "source": "historical data",
                "correlation_tag": "market_volatility",
            }
        }
    )


class CategoryRequest(BaseModel):
    """Input model for category identification."""

    business_context: BusinessContext = Field(
        description="Business context information"
    )
    existing_categories: Optional[List[str]] = Field(
        default=None, description="List of existing categories to consider"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "business_context": {
                    "project_id": "CRM-2023",
                    "project_description": "Implementation of a new CRM system",
                    "language": "en",
                },
                "existing_categories": ["Technical", "Organizational"],
            }
        }
    )


class CategoryResponse(BaseResponse):
    """Output model for identified categories."""

    categories: List[str] = Field(description="List of identified risk categories")
    rationale: Optional[str] = Field(
        default=None, description="Explanation for the identified categories"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "categories": ["Technical", "Organizational", "Financial", "Legal"],
                "rationale": "These categories cover the main risk areas for a CRM implementation project.",
                "model_version": "1.0",
                "response_info": {
                    "consumed_tokens": 1250,
                    "total_cost": 0.025,
                    "prompt_name": "get_categories",
                    "model_name": "gpt-4",
                },
            }
        }
    )


class RiskRequest(BaseModel):
    """Input model for risk identification."""

    business_context: BusinessContext = Field(
        description="Business context information"
    )
    category: str = Field(description="Risk category to identify risks for")
    max_risks: Optional[int] = Field(
        default=5, description="Maximum number of risks to identify", ge=1, le=20
    )
    existing_risks: Optional[List[str]] = Field(
        default=None, description="List of existing risks to consider"
    )

    @field_validator("max_risks")
    @classmethod
    def validate_max_risks(cls, v):
        if v is not None and (v < 1 or v > 20):
            raise ValueError("max_risks must be between 1 and 20")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "business_context": {
                    "project_id": "CRM-2023",
                    "project_description": "Implementation of a new CRM system",
                    "language": "en",
                },
                "category": "Technical",
                "max_risks": 5,
                "existing_risks": ["Data migration failure"],
            }
        }
    )


class Risk(BaseModel):
    """Representation of a single risk."""

    title: str = Field(description="Short title of the risk")
    description: str = Field(description="Detailed description of the risk")
    category: str = Field(description="Category the risk belongs to")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Data Migration Failure",
                "description": "Risk of losing critical customer data during migration to the new CRM system",
                "category": "Technical",
            }
        }
    )


class RiskResponse(BaseResponse):
    """Output model for identified risks."""

    risks: List[Risk] = Field(description="List of identified risks")
    references: Optional[List[str]] = Field(
        default=None, description="References used for risk identification"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "risks": [
                    {
                        "title": "Data Migration Failure",
                        "description": "Risk of losing critical customer data during migration to the new CRM system",
                        "category": "Technical",
                    },
                    {
                        "title": "User Adoption Issues",
                        "description": "Risk of low user adoption due to resistance to change",
                        "category": "Organizational",
                    },
                ],
                "references": [
                    "Industry report on CRM implementations",
                    "Internal lessons learned",
                ],
                "model_version": "1.0",
                "response_info": {
                    "consumed_tokens": 1500,
                    "total_cost": 0.03,
                    "prompt_name": "get_risks",
                    "model_name": "gpt-4",
                },
            }
        }
    )


class DefinitionCheckRequest(BaseModel):
    """Input model for checking and revising a risk definition."""

    business_context: BusinessContext = Field(
        description="Business context information"
    )
    risk_description: str = Field(description="Risk description to check and revise")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "business_context": {
                    "project_id": "CRM-2023",
                    "project_description": "Implementation of a new CRM system",
                    "language": "en",
                },
                "risk_description": "The project may fail due to technical issues.",
            }
        }
    )


class DefinitionCheckResponse(BaseResponse):
    """Output model for a revised risk definition."""

    revised_description: str = Field(description="Revised risk description")
    biases: Optional[List[str]] = Field(
        default=None, description="List of identified biases in the risk description"
    )
    rationale: Optional[str] = Field(
        default=None, description="Rationale for the revisions made"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "revised_description": "There is a 30% probability that the CRM implementation will experience critical technical failures within the first 3 months of deployment.",
                "biases": ["ambiguous wording", "missing quantifiers"],
                "rationale": "The original description was too vague and lacked specific quantifiers.",
                "model_version": "1.0",
                "response_info": {
                    "consumed_tokens": 1200,
                    "total_cost": 0.024,
                    "prompt_name": "check_definition",
                    "model_name": "gpt-4",
                },
            }
        }
    )


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


class AssessmentRequest(BaseModel):
    """Input model for assessing a risk's impact."""

    business_context: BusinessContext = Field(
        description="Business context information"
    )
    risk_description: str = Field(description="Risk description to assess")

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


class QuantitativeAssessment(BaseModel):
    """Nested model for quantitative risk assessment."""

    minimum: Optional[float] = Field(
        default=None, description="Minimum value of the risk assessment"
    )
    most_likely: Optional[float] = Field(
        default=None, description="Most likely value of the risk assessment"
    )
    maximum: Optional[float] = Field(
        default=None, description="Maximum value of the risk assessment"
    )
    distribution: Optional[str] = Field(
        default=None, description="Distribution type (e.g., normal, triangular)"
    )
    distribution_fit: Optional[Dist] = Field(
        default=None, description="Fitted distribution parameters"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "minimum": 50000.0,
                "most_likely": 100000.0,
                "maximum": 200000.0,
                "distribution": "triangular",
                "distribution_fit": {
                    "name": "triangular",
                    "parameters": {"min": 50000.0, "mode": 100000.0, "max": 200000.0},
                },
            }
        }
    )


class AssessmentResponse(BaseResponse):
    """Output model for a risk impact assessment."""

    quantitative: Optional[QuantitativeAssessment] = Field(
        default=None, description="Quantitative assessment details"
    )
    impact: Optional[float] = Field(
        default=None, description="Impact score (0-1 or monetary value)"
    )
    probability: Optional[float] = Field(
        default=None, description="Probability score (0-1)"
    )
    evidence: Optional[str] = Field(
        default=None, description="Evidence supporting the assessment"
    )
    references: Optional[List[str]] = Field(
        default=None, description="References used for the assessment"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "quantitative": {
                    "minimum": 50000.0,
                    "most_likely": 100000.0,
                    "maximum": 200000.0,
                    "distribution": "triangular",
                },
                "impact": 0.7,
                "probability": 0.3,
                "evidence": "Based on historical data from similar CRM implementations",
                "references": [
                    "Industry report on CRM implementations",
                    "Internal lessons learned",
                ],
                "model_version": "1.0",
                "response_info": {
                    "consumed_tokens": 1400,
                    "total_cost": 0.028,
                    "prompt_name": "get_assessment",
                    "model_name": "gpt-4",
                },
            }
        }
    )


class MitigationRequest(BaseModel):
    """Input model for risk mitigation measures."""

    business_context: BusinessContext
    risk_description: str
    drivers: Optional[List[str]] = None


class MitigationResponse(BaseModel):
    """Output model containing mitigation measures."""

    mitigations: List[str]
    references: Optional[List[str]] = None
    response_info: Optional[ResponseInfo] = None


class PrioritizationRequest(BaseModel):
    """Input model for prioritizing risks."""

    business_context: BusinessContext
    risks: List[str]


class PrioritizationResponse(BaseModel):
    """Output model containing prioritized risks."""

    prioritized_risks: List[str]
    rationale: Optional[str] = None
    response_info: Optional[ResponseInfo] = None


class CostBenefitRequest(BaseModel):
    """Input for cost-benefit analysis of mitigations."""

    business_context: BusinessContext
    risk_description: str
    mitigations: List[str]


class CostBenefit(BaseModel):
    mitigation: str
    cost: Optional[str] = None
    benefit: Optional[str] = None


class CostBenefitResponse(BaseModel):
    analyses: List[CostBenefit]
    references: Optional[List[str]] = None
    response_info: Optional[ResponseInfo] = None


class MonitoringRequest(BaseModel):
    """Input for deriving monitoring indicators."""

    business_context: BusinessContext
    risk_description: str


class MonitoringResponse(BaseModel):
    indicators: List[str]
    references: Optional[List[str]] = None
    response_info: Optional[ResponseInfo] = None


class OpportunityRequest(BaseModel):
    """Input for identifying opportunities."""

    business_context: BusinessContext
    risks: List[str]


class OpportunityResponse(BaseModel):
    opportunities: List[str]
    references: Optional[List[str]] = None
    response_info: Optional[ResponseInfo] = None


class CommunicationRequest(BaseModel):
    """Input for summarising risks for stakeholders."""

    business_context: BusinessContext
    summary: str


class CommunicationResponse(BaseModel):
    executive_summary: str
    technical_annex: Optional[str] = None
    response_info: Optional[ResponseInfo] = None


class BiasCheckRequest(BaseModel):
    """Input for checking risk description biases."""

    business_context: Optional[BusinessContext] = None
    risk_description: str


class BiasCheckResponse(BaseModel):
    biases: List[str]
    suggestions: Optional[str] = None
    response_info: Optional[ResponseInfo] = None


class CorrelationTagRequest(BaseModel):
    """Input model for defining correlation tags."""

    business_context: BusinessContext
    risk_titles: List[str]
    known_drivers: Optional[List[str]] = None


class CorrelationTagResponse(BaseModel):
    tags: List[str]
    rationale: Optional[str] = None
    response_info: Optional[ResponseInfo] = None


class AudienceEnum(str, Enum):
    """Supported audiences for presentation output."""

    executive = "executive"
    workshop = "workshop"
    risk_internal = "risk_internal"
    audit = "audit"
    regulator = "regulator"
    project_owner = "project_owner"
    investor = "investor"
    operations = "operations"


class PresentationRequest(BaseModel):
    """Input model for presentation-oriented summaries."""

    business_context: BusinessContext
    audience: AudienceEnum
    focus_areas: Optional[List[str]] = None


class PresentationResponse(BaseModel):
    """Structured output for presentation-ready summaries."""

    executive_summary: str
    main_risks: List[str]
    quantitative_summary: Optional[str] = None
    key_drivers: Optional[List[str]] = None
    correlation_tags: Optional[List[str]] = None
    mitigations: Optional[List[str]] = None
    open_questions: Optional[List[str]] = None
    chart_placeholders: Optional[List[str]] = None
    appendix: Optional[str] = None
    response_info: Optional[ResponseInfo] = None


class SourceEntry(BaseModel):
    """Structured reference to an external source."""

    title: str
    url: str
    date: Optional[str] = None
    type: Optional[str] = None
    comment: Optional[str] = None


class ExternalContextRequest(BaseModel):
    """Input model for external context enrichment."""

    business_context: BusinessContext
    focus_keywords: Optional[List[str]] = None
    time_horizon_months: Optional[int] = 12


class ExternalContextResponse(BaseModel):
    """Output model containing summarised external information."""

    sector_summary: str
    external_risks: List[str]
    source_table: List[Dict[str, str]]
    workshop_recommendations: List[str]
    full_report: Optional[str] = None
    response_info: Optional[ResponseInfo] = None


class ContextQualityRequest(BaseModel):
    """Input model for evaluating context knowledge."""

    business_context: BusinessContext
    project_type: Optional[str] = None


class ContextQualityResponse(BaseModel):
    """Output model describing context quality."""

    shortcomings: List[str]
    rationale: str
    suggested_improvements: str
    response_info: Optional[ResponseInfo] = None
