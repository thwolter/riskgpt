# Risk Schema Models

This page documents the schema models related to risk identification and management in the RiskGPT application.

## Overview

The risk schema models define the structure for risk identification requests and responses. They are used in the risk workflow and related chains.

## Models

### Risk

```python
class Risk(BaseModel):
    title: str = Field(description="Short title of the risk")
    description: str = Field(description="Detailed description of the risk")
    category: str = Field(description="Category the risk belongs to")
    document_refs: Optional[List[str]] = Field(
        default=None,
        description="References to document UUIDs from the document microservice",
    )
```

Representation of a single risk.

**Fields:**
- `title` (str): Short title of the risk
- `description` (str): Detailed description of the risk
- `category` (str): Category the risk belongs to
- `document_refs` (Optional[List[str]]): References to document UUIDs from the document microservice

**Example:**
```python
{
    "title": "Data Migration Failure",
    "description": "Risk of losing critical customer data during migration to the new CRM system",
    "category": "Technical"
}
```

### RiskRequest

```python
class RiskRequest(BaseModel):
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
    document_refs: Optional[List[str]] = Field(
        default=None,
        description="References to document UUIDs from the document microservice",
    )
```

Input model for risk identification.

**Fields:**
- `business_context` (BusinessContext): Business context information
- `category` (str): Risk category to identify risks for
- `max_risks` (Optional[int]): Maximum number of risks to identify (between 1 and 20, default 5)
- `existing_risks` (Optional[List[str]]): List of existing risks to consider
- `document_refs` (Optional[List[str]]): References to document UUIDs from the document microservice

**Example:**
```python
{
    "business_context": {
        "project_id": "CRM-2023",
        "project_description": "Implementation of a new CRM system",
        "language": "en",
    },
    "category": "Technical",
    "max_risks": 5,
    "existing_risks": ["Data migration failure"],
}
```

### RiskResponse

```python
class RiskResponse(BaseResponse):
    risks: List[Risk] = Field(description="List of identified risks")
    references: Optional[List[str]] = Field(
        default=None, description="References used for risk identification"
    )
    document_refs: Optional[List[str]] = Field(
        default=None,
        description="References to document UUIDs from the document microservice",
    )
```

Output model for identified risks.

**Fields:**
- `risks` (List[Risk]): List of identified risks
- `references` (Optional[List[str]]): References used for risk identification
- `document_refs` (Optional[List[str]]): References to document UUIDs from the document microservice
- `model_version` (str): Schema version for backward compatibility (inherited from BaseResponse)
- `response_info` (Optional[ResponseInfo]): Information about the response processing (inherited from BaseResponse)

**Example:**
```python
{
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
```

### DefinitionCheckRequest

```python
class DefinitionCheckRequest(BaseModel):
    business_context: BusinessContext = Field(
        description="Business context information"
    )
    risk_description: str = Field(description="Risk description to check and revise")
```

Input model for checking and revising a risk definition.

**Fields:**
- `business_context` (BusinessContext): Business context information
- `risk_description` (str): Risk description to check and revise

**Example:**
```python
{
    "business_context": {
        "project_id": "CRM-2023",
        "project_description": "Implementation of a new CRM system",
        "language": "en",
    },
    "risk_description": "The project may fail due to technical issues.",
}
```

### DefinitionCheckResponse

```python
class DefinitionCheckResponse(BaseResponse):
    revised_description: str = Field(description="Revised risk description")
    biases: Optional[List[str]] = Field(
        default=None, description="List of identified biases in the risk description"
    )
    rationale: Optional[str] = Field(
        default=None, description="Rationale for the revisions made"
    )
```

Output model for a revised risk definition.

**Fields:**
- `revised_description` (str): Revised risk description
- `biases` (Optional[List[str]]): List of identified biases in the risk description
- `rationale` (Optional[str]): Rationale for the revisions made
- `model_version` (str): Schema version for backward compatibility (inherited from BaseResponse)
- `response_info` (Optional[ResponseInfo]): Information about the response processing (inherited from BaseResponse)

**Example:**
```python
{
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
```

## Usage

These models are used in the risk workflow and related chains to identify and manage risks.

### Risk Identification

```python
from src.models.schemas import BusinessContext, RiskRequest
from src.workflows import risk_workflow

# Create a request
request = RiskRequest(
    business_context=BusinessContext(
        project_id="PRJ-2023-001",
        project_description="Implementation of a new CRM system",
        domain_knowledge="The company operates in the B2B sector",
    ),
    category="Technical",
    max_risks=5,
)

# Run the workflow
response = risk_workflow(request)

# Access the results
for risk in response.risks:
    print(f"Risk: {risk.title}")
    print(f"Description: {risk.description}")
    print(f"Category: {risk.category}")
    print("---")
```

### Definition Check

```python
from src.models.schemas import BusinessContext, DefinitionCheckRequest
from src.chains import check_definition_chain

# Create a request
request = DefinitionCheckRequest(
    business_context=BusinessContext(
        project_id="PRJ-2023-001",
        project_description="Implementation of a new CRM system",
    ),
    risk_description="The project may fail due to technical issues.",
)

# Run the chain
response = check_definition_chain(request)

# Access the results
print(f"Original: {request.risk_description}")
print(f"Revised: {response.revised_description}")
if response.biases:
    print(f"Biases: {', '.join(response.biases)}")
if response.rationale:
    print(f"Rationale: {response.rationale}")
```