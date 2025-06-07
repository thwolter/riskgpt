from pydantic import BaseModel
from typing import List, Optional

class Prompt(BaseModel):
    version: str
    description: str
    template: str

class ResponseInfo(BaseModel):
    consumed_tokens: int
    total_cost: float
    prompt_name: str
    model_name: str

class CategoryRequest(BaseModel):
    project_id: str
    project_description: str
    domain_knowledge: Optional[str] = None
    language: Optional[str] = "en"

class CategoryResponse(BaseModel):
    categories: List[str]
    rationale: Optional[str]
    response_info: Optional[ResponseInfo] = None


class RiskRequest(BaseModel):
    """Input model for risk identification."""

    project_id: str
    project_description: str
    category: str
    domain_knowledge: Optional[str] = None
    language: Optional[str] = "en"


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

    project_id: str
    risk_description: str
    domain_knowledge: Optional[str] = None
    language: Optional[str] = "en"


class DefinitionCheckResponse(BaseModel):
    """Output model for a revised risk definition."""

    revised_description: str
    rationale: Optional[str] = None
    response_info: Optional[ResponseInfo] = None


class DriverRequest(BaseModel):
    """Input model for risk driver identification."""

    project_id: str
    risk_description: str
    domain_knowledge: Optional[str] = None
    language: Optional[str] = "en"


class DriverResponse(BaseModel):
    """Output model containing risk drivers."""

    drivers: List[str]
    references: Optional[List[str]] = None
    response_info: Optional[ResponseInfo] = None


class ImpactRequest(BaseModel):
    """Input model for estimating risk impact."""

    project_id: str
    risk_description: str
    domain_knowledge: Optional[str] = None
    language: Optional[str] = "en"


class ImpactResponse(BaseModel):
    """Output model for a three-point impact estimate."""

    minimum: float
    most_likely: float
    maximum: float
    distribution: str
    references: Optional[List[str]] = None
    response_info: Optional[ResponseInfo] = None


class AssessmentRequest(BaseModel):
    """Input model for assessing a risk's impact."""

    project_id: str
    risk_description: str
    domain_knowledge: Optional[str] = None
    language: Optional[str] = "en"


class AssessmentResponse(BaseModel):
    """Output model for a risk impact assessment."""

    minimum: Optional[float] = None
    most_likely: Optional[float] = None
    maximum: Optional[float] = None
    distribution: Optional[str] = None
    impact: Optional[float] = None
    probability: Optional[float] = None
    evidence: Optional[str] = None
    references: Optional[List[str]] = None
    response_info: Optional[ResponseInfo] = None


class MitigationRequest(BaseModel):
    """Input model for risk mitigation measures."""

    project_id: str
    risk_description: str
    drivers: Optional[List[str]] = None
    domain_knowledge: Optional[str] = None
    language: Optional[str] = "en"


class MitigationResponse(BaseModel):
    """Output model containing mitigation measures."""

    mitigations: List[str]
    references: Optional[List[str]] = None
    response_info: Optional[ResponseInfo] = None
