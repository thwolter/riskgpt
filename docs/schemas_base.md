# Base Schema Models

This page documents the base schema models used throughout the RiskGPT application.

## Overview

The base schema models provide the foundation for all other models in the application. They define common structures and fields that are reused across different parts of the application.

## Models

### Prompt

```python
class Prompt(BaseModel):
    version: str
    description: str
    template: str
```

A model representing a prompt template with version information and description.

**Fields:**
- `version` (str): Version of the prompt template
- `description` (str): Description of what the prompt does
- `template` (str): The actual prompt template text

### LanguageEnum

```python
class LanguageEnum(str, Enum):
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
```

An enumeration of supported languages for responses.

### ResponseInfo

```python
class ResponseInfo(BaseModel):
    consumed_tokens: int
    total_cost: float
    prompt_name: str
    model_name: str
    error: Optional[str] = None
```

Information about the response processing, including token usage and cost.

**Fields:**
- `consumed_tokens` (int): Number of tokens consumed by the request
- `total_cost` (float): Total cost of the request
- `prompt_name` (str): Name of the prompt used
- `model_name` (str): Name of the model used
- `error` (Optional[str]): Error message, if any

### BaseResponse

```python
class BaseResponse(BaseModel):
    model_version: str = Field(
        default="1.0", description="Schema version for backward compatibility"
    )
    response_info: Optional[ResponseInfo] = Field(
        default=None, description="Information about the response processing"
    )
```

Base class for all response models, providing common fields.

**Fields:**
- `model_version` (str): Schema version for backward compatibility
- `response_info` (Optional[ResponseInfo]): Information about the response processing

### BusinessContext

```python
class BusinessContext(BaseModel):
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
    document_refs: Optional[List[str]] = Field(
        default=None,
        description="References to document UUIDs from the document microservice",
    )
```

Standardized schema for business context information.

**Fields:**
- `model_version` (str): Schema version for backward compatibility
- `project_id` (str): Unique identifier for the project
- `project_description` (Optional[str]): Detailed description of the project
- `domain_knowledge` (Optional[str]): Specific domain knowledge relevant to the project
- `business_area` (Optional[str]): Business area or department the project belongs to
- `industry_sector` (Optional[str]): Industry sector the project operates in
- `language` (Optional[LanguageEnum]): Language for the response
- `document_refs` (Optional[List[str]]): References to document UUIDs from the document microservice

**Methods:**
- `get_domain_section()`: Return formatted domain knowledge section if available

### Dist

```python
class Dist(BaseModel):
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
```

Generic distribution model for statistical distributions.

**Fields:**
- `name` (str): Name of the distribution
- `parameters` (Optional[Dict[str, float]]): Parameters of the distribution
- `source` (Optional[str]): Source of the distribution
- `correlation_tag` (Optional[str]): Tag for correlation analysis

**Example:**
```python
{
    "name": "normal",
    "parameters": {"mean": 100.0, "std": 10.0},
    "source": "historical data",
    "correlation_tag": "market_volatility"
}
```

## Usage

These base models are used throughout the application as building blocks for more complex models. For example, the `BusinessContext` model is used in almost all request models to provide context for the request.

```python
from riskgpt.models.schemas import BusinessContext

# Create a business context
context = BusinessContext(
    project_id="PRJ-2023-001",
    project_description="Implementation of a new CRM system",
    domain_knowledge="The company operates in the B2B sector",
    business_area="IT",
    industry_sector="Finance",
    language="en",
)

# Use the business context in a request
from riskgpt.models.schemas import RiskRequest

request = RiskRequest(
    business_context=context,
    category="Technical",
    max_risks=5,
)
```