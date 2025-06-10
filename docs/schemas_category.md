# Category Schema Models

This page documents the schema models related to risk categories in the RiskGPT application.

## Overview

The category schema models define the structure for risk category identification requests and responses. Risk categories help organize risks into logical groups for better management and analysis.

## Models

### CategoryRequest

```python
class CategoryRequest(BaseModel):
    business_context: BusinessContext = Field(
        description="Business context information"
    )
    existing_categories: Optional[List[str]] = Field(
        default=None, description="List of existing categories to consider"
    )
```

Input model for category identification.

**Fields:**
- `business_context` (BusinessContext): Business context information
- `existing_categories` (Optional[List[str]]): List of existing categories to consider

**Example:**
```python
{
    "business_context": {
        "project_id": "CRM-2023",
        "project_description": "Implementation of a new CRM system",
        "language": "en",
    },
    "existing_categories": ["Technical", "Organizational"],
}
```

### CategoryResponse

```python
class CategoryResponse(BaseResponse):
    categories: List[str] = Field(description="List of identified risk categories")
    rationale: Optional[str] = Field(
        default=None, description="Explanation for the identified categories"
    )
```

Output model for identified categories.

**Fields:**
- `categories` (List[str]): List of identified risk categories
- `rationale` (Optional[str]): Explanation for the identified categories
- `model_version` (str): Schema version for backward compatibility (inherited from BaseResponse)
- `response_info` (Optional[ResponseInfo]): Information about the response processing (inherited from BaseResponse)

**Example:**
```python
{
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
```

### CorrelationTagRequest

```python
class CorrelationTagRequest(BaseModel):
    business_context: BusinessContext
    risk_titles: List[str]
    known_drivers: Optional[List[str]] = None
```

Input model for defining correlation tags.

**Fields:**
- `business_context` (BusinessContext): Business context information
- `risk_titles` (List[str]): List of risk titles to analyze for correlation
- `known_drivers` (Optional[List[str]]): List of known drivers to consider

**Example:**
```python
{
    "business_context": {
        "project_id": "CRM-2023",
        "project_description": "Implementation of a new CRM system",
        "language": "en",
    },
    "risk_titles": [
        "Data Migration Failure",
        "User Adoption Issues",
        "Integration Problems",
    ],
    "known_drivers": [
        "Inadequate testing",
        "Resistance to change",
        "Technical complexity",
    ],
}
```

### CorrelationTagResponse

```python
class CorrelationTagResponse(BaseModel):
    tags: List[str]
    rationale: Optional[str] = None
    response_info: Optional[ResponseInfo] = None
```

Output model for correlation tags.

**Fields:**
- `tags` (List[str]): List of correlation tags
- `rationale` (Optional[str]): Explanation for the identified tags
- `response_info` (Optional[ResponseInfo]): Information about the response processing

**Example:**
```python
{
    "tags": [
        "technical_complexity",
        "change_management",
        "data_quality",
    ],
    "rationale": "These tags represent common factors that could affect multiple risks in the project.",
    "response_info": {
        "consumed_tokens": 1100,
        "total_cost": 0.022,
        "prompt_name": "get_correlation_tags",
        "model_name": "gpt-4",
    },
}
```

## Usage

These models are used in the category identification and correlation tag chains to organize risks and identify common factors.

### Category Identification

```python
from riskgpt.models.schemas import BusinessContext, CategoryRequest
from riskgpt.chains import get_categories_chain

# Create a request
request = CategoryRequest(
    business_context=BusinessContext(
        project_id="PRJ-2023-001",
        project_description="Implementation of a new CRM system",
        domain_knowledge="The company operates in the B2B sector",
    ),
    existing_categories=["Technical", "Organizational"],
)

# Run the chain
response = get_categories_chain(request)

# Access the results
print("Risk Categories:")
for category in response.categories:
    print(f"- {category}")
if response.rationale:
    print(f"\nRationale: {response.rationale}")
```

### Correlation Tag Identification

```python
from riskgpt.models.schemas import BusinessContext, CorrelationTagRequest
from riskgpt.chains import get_correlation_tags_chain

# Create a request
request = CorrelationTagRequest(
    business_context=BusinessContext(
        project_id="PRJ-2023-001",
        project_description="Implementation of a new CRM system",
        domain_knowledge="The company operates in the B2B sector",
    ),
    risk_titles=[
        "Data Migration Failure",
        "User Adoption Issues",
        "Integration Problems",
    ],
    known_drivers=[
        "Inadequate testing",
        "Resistance to change",
        "Technical complexity",
    ],
)

# Run the chain
response = get_correlation_tags_chain(request)

# Access the results
print("Correlation Tags:")
for tag in response.tags:
    print(f"- {tag}")
if response.rationale:
    print(f"\nRationale: {response.rationale}")
```

### Categories in Risk Workflow

The category models are used in the risk workflow to identify risks for specific categories:

```python
from riskgpt.models.schemas import BusinessContext, RiskRequest
from riskgpt.workflows import risk_workflow

# First identify categories
from riskgpt.chains import get_categories_chain
category_request = CategoryRequest(
    business_context=BusinessContext(
        project_id="PRJ-2023-001",
        project_description="Implementation of a new CRM system",
        domain_knowledge="The company operates in the B2B sector",
    ),
)
category_response = get_categories_chain(category_request)

# Then identify risks for each category
for category in category_response.categories:
    risk_request = RiskRequest(
        business_context=category_request.business_context,
        category=category,
        max_risks=5,
    )
    risk_response = risk_workflow(risk_request)
    
    print(f"\nRisks for category '{category}':")
    for risk in risk_response.risks:
        print(f"- {risk.title}")
```