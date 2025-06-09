from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class Prompt(BaseModel):
    version: str
    description: str
    template: str


class ResponseInfo(BaseModel):
    consumed_tokens: int
    total_cost: float
    prompt_name: str
    model_name: str
    error: Optional[str] = None


class BusinessContext(BaseModel):
    """Standardized schema for business context information."""

    project_id: str = Field(description="Unique identifier for the project")
    project_description: Optional[str] = Field(
        default=None, description="Detailed description of the project"
    )
    domain_knowledge: Optional[str] = Field(
        default=None, description="Specific domain knowledge relevant to the project"
    )
    business_area: Optional[str] = Field(
        default=None, description="Business area or department the project belongs to"
    )
    industry_sector: Optional[str] = Field(
        default=None, description="Industry sector the project operates in"
    )
    language: Optional[str] = Field(
        default="en", description="Language for the response"
    )


class Dist(BaseModel):
    """Generic distribution model."""

    name: str
    parameters: Optional[Dict[str, float]] = None
    source: Optional[str] = None
    correlation_tag: Optional[str] = None


class CategoryRequest(BaseModel):
    business_context: BusinessContext
    existing_categories: Optional[List[str]] = None


class CategoryResponse(BaseModel):
    categories: List[str]
    rationale: Optional[str]
    response_info: Optional[ResponseInfo] = None


class RiskRequest(BaseModel):
    """Input model for risk identification."""

    business_context: BusinessContext
    category: str
    max_risks: Optional[int] = 5
    existing_risks: Optional[List[str]] = None


class Risk(BaseModel):
    """Representation of a single risk."""

    title: str
    description: str
    category: str


class RiskResponse(BaseModel):
    """Output model for identified risks."""

    risks: List[Risk]
    references: Optional[List[str]] = None
    response_info: Optional[ResponseInfo] = None


class DefinitionCheckRequest(BaseModel):
    """Input model for checking and revising a risk definition."""

    business_context: BusinessContext
    risk_description: str


class DefinitionCheckResponse(BaseModel):
    """Output model for a revised risk definition."""

    revised_description: str
    biases: Optional[List[str]] = None
    rationale: Optional[str] = None
    response_info: Optional[ResponseInfo] = None


class DriverRequest(BaseModel):
    """Input model for risk driver identification."""

    business_context: BusinessContext
    risk_description: str


class DriverResponse(BaseModel):
    """Output model containing risk drivers."""

    drivers: List[str]
    references: Optional[List[str]] = None
    response_info: Optional[ResponseInfo] = None


class AssessmentRequest(BaseModel):
    """Input model for assessing a risk's impact."""

    business_context: BusinessContext
    risk_description: str


class AssessmentResponse(BaseModel):
    """Output model for a risk impact assessment."""

    minimum: Optional[float] = None
    most_likely: Optional[float] = None
    maximum: Optional[float] = None
    distribution: Optional[str] = None
    distribution_fit: Optional[Dist] = None
    impact: Optional[float] = None
    probability: Optional[float] = None
    evidence: Optional[str] = None
    references: Optional[List[str]] = None
    response_info: Optional[ResponseInfo] = None


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
