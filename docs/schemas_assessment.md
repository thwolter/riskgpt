# Assessment Schema Models

This page documents the schema models related to risk assessment in the RiskGPT application.

## Overview

The assessment schema models define the structure for risk assessment requests and responses. They are used in the risk assessment workflow and related chains.

## Models

### QuantitativeAssessment

```python
class QuantitativeAssessment(BaseModel):
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
```

Nested model for quantitative risk assessment.

**Fields:**
- `minimum` (Optional[float]): Minimum value of the risk assessment
- `most_likely` (Optional[float]): Most likely value of the risk assessment
- `maximum` (Optional[float]): Maximum value of the risk assessment
- `distribution` (Optional[str]): Distribution type (e.g., normal, triangular)
- `distribution_fit` (Optional[Dist]): Fitted distribution parameters

**Example:**
```python
{
    "minimum": 50000.0,
    "most_likely": 100000.0,
    "maximum": 200000.0,
    "distribution": "triangular",
    "distribution_fit": {
        "name": "triangular",
        "parameters": {"min": 50000.0, "mode": 100000.0, "max": 200000.0},
    },
}
```

### AssessmentRequest

```python
class AssessmentRequest(BaseModel):
    business_context: BusinessContext = Field(
        description="Business context information"
    )
    risk_description: str = Field(description="Risk description to assess")
    document_refs: Optional[List[str]] = Field(
        default=None,
        description="References to document UUIDs from the document microservice",
    )
```

Input model for assessing a risk's impact.

**Fields:**
- `business_context` (BusinessContext): Business context information
- `risk_description` (str): Risk description to assess
- `document_refs` (Optional[List[str]]): References to document UUIDs from the document microservice

**Example:**
```python
{
    "business_context": {
        "project_id": "CRM-2023",
        "project_description": "Implementation of a new CRM system",
        "language": "en",
    },
    "risk_description": "There is a 30% probability that the CRM implementation will experience critical technical failures within the first 3 months of deployment.",
}
```

### AssessmentResponse

```python
class AssessmentResponse(BaseResponse):
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
    document_refs: Optional[List[str]] = Field(
        default=None,
        description="References to document UUIDs from the document microservice",
    )
```

Output model for a risk impact assessment.

**Fields:**
- `quantitative` (Optional[QuantitativeAssessment]): Quantitative assessment details
- `impact` (Optional[float]): Impact score (0-1 or monetary value)
- `probability` (Optional[float]): Probability score (0-1)
- `evidence` (Optional[str]): Evidence supporting the assessment
- `references` (Optional[List[str]]): References used for the assessment
- `document_refs` (Optional[List[str]]): References to document UUIDs from the document microservice
- `model_version` (str): Schema version for backward compatibility (inherited from BaseResponse)
- `response_info` (Optional[ResponseInfo]): Information about the response processing (inherited from BaseResponse)

**Example:**
```python
{
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
```

## Usage

These models are used in the risk assessment workflow and related chains to assess the impact and probability of identified risks.

### Risk Assessment

```python
from riskgpt.models.schemas import BusinessContext, AssessmentRequest
from riskgpt.chains import get_assessment_chain

# Create a request
request = AssessmentRequest(
    business_context=BusinessContext(
        project_id="PRJ-2023-001",
        project_description="Implementation of a new CRM system",
        domain_knowledge="The company operates in the B2B sector",
    ),
    risk_description="There is a 30% probability that the CRM implementation will experience critical technical failures within the first 3 months of deployment.",
)

# Run the chain
response = get_assessment_chain(request)

# Access the results
print(f"Impact: {response.impact}")
print(f"Probability: {response.probability}")
if response.evidence:
    print(f"Evidence: {response.evidence}")
if response.quantitative:
    print(f"Quantitative Assessment:")
    print(f"  Minimum: {response.quantitative.minimum}")
    print(f"  Most Likely: {response.quantitative.most_likely}")
    print(f"  Maximum: {response.quantitative.maximum}")
    print(f"  Distribution: {response.quantitative.distribution}")
```

### Assessment in Risk Workflow

The assessment models are also used in the risk workflow:

```python
from riskgpt.models.schemas import BusinessContext, RiskRequest
from riskgpt.workflows import risk_workflow

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

# Run the workflow (includes assessment)

response = risk_workflow(request)

# The assessments are performed internally in the workflow
# but are not directly accessible in the response
# You would need to call get_assessment_chain separately for each risk
```