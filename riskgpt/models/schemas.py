from pydantic import BaseModel
from typing import List, Optional

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
