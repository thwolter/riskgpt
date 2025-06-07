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
