# Driver Schema Models

This page documents the schema models related to risk drivers in the RiskGPT application.

## Overview

The driver schema models define the structure for risk driver identification requests and responses. Risk drivers are factors that contribute to or influence the likelihood or impact of a risk.

## Models

### DriverRequest

```python
class DriverRequest(BaseModel):
    business_context: BusinessContext = Field(
        description="Business context information"
    )
    risk_description: str = Field(
        description="Risk description to identify drivers for"
    )
```

Input model for risk driver identification.

**Fields:**
- `business_context` (BusinessContext): Business context information
- `risk_description` (str): Risk description to identify drivers for

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

### DriverResponse

```python
class DriverResponse(BaseResponse):
    drivers: List[str] = Field(description="List of identified risk drivers")
    references: Optional[List[str]] = Field(
        default=None, description="References used for driver identification"
    )
```

Output model containing risk drivers.

**Fields:**
- `drivers` (List[str]): List of identified risk drivers
- `references` (Optional[List[str]]): References used for driver identification
- `model_version` (str): Schema version for backward compatibility (inherited from BaseResponse)
- `response_info` (Optional[ResponseInfo]): Information about the response processing (inherited from BaseResponse)

**Example:**
```python
{
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
        "prompt_name": "risk_drivers",
        "model_name": "gpt-4",
    },
}
```

### MitigationRequest

```python
class MitigationRequest(BaseModel):
    business_context: BusinessContext
    risk_description: str
    drivers: Optional[List[str]] = None
```

Input model for risk mitigation measures.

**Fields:**
- `business_context` (BusinessContext): Business context information
- `risk_description` (str): Risk description to identify mitigation measures for
- `drivers` (Optional[List[str]]): List of risk drivers to consider for mitigation

**Example:**
```python
{
    "business_context": {
        "project_id": "CRM-2023",
        "project_description": "Implementation of a new CRM system",
        "language": "en",
    },
    "risk_description": "There is a 30% probability that the CRM implementation will experience critical technical failures within the first 3 months of deployment.",
    "drivers": [
        "Inadequate testing before deployment",
        "Incompatibility with existing systems",
        "Poor data quality in source systems",
    ],
}
```

### MitigationResponse

```python
class MitigationResponse(BaseModel):
    mitigations: List[str]
    references: Optional[List[str]] = None
    response_info: Optional[ResponseInfo] = None
```

Output model containing mitigation measures.

**Fields:**
- `mitigations` (List[str]): List of mitigation measures
- `references` (Optional[List[str]]): References used for mitigation identification
- `response_info` (Optional[ResponseInfo]): Information about the response processing

**Example:**
```python
{
    "mitigations": [
        "Implement comprehensive testing plan including unit, integration, and user acceptance testing",
        "Conduct thorough compatibility assessment with existing systems before deployment",
        "Perform data quality assessment and cleansing of source data before migration",
    ],
    "references": [
        "Industry best practices for CRM implementations",
        "Internal testing guidelines",
    ],
    "response_info": {
        "consumed_tokens": 1350,
        "total_cost": 0.027,
        "prompt_name": "risk_mitigations",
        "model_name": "gpt-4",
    },
}
```

## Usage

These models are used in the driver identification and mitigation chains to identify factors that contribute to risks and suggest mitigation measures.

### Driver Identification

```python
from src.models.schemas import BusinessContext, DriverRequest
from src.chains import get_drivers_chain

# Create a request
request = DriverRequest(
    business_context=BusinessContext(
        project_id="PRJ-2023-001",
        project_description="Implementation of a new CRM system",
        domain_knowledge="The company operates in the B2B sector",
    ),
    risk_description="There is a 30% probability that the CRM implementation will experience critical technical failures within the first 3 months of deployment.",
)

# Run the chain
response = get_drivers_chain(request)

# Access the results
print("Risk Drivers:")
for driver in response.drivers:
    print(f"- {driver}")
```

### Mitigation Identification

```python
from src.models.schemas import BusinessContext, MitigationRequest
from src.chains import get_mitigations_chain

# Create a request
request = MitigationRequest(
    business_context=BusinessContext(
        project_id="PRJ-2023-001",
        project_description="Implementation of a new CRM system",
        domain_knowledge="The company operates in the B2B sector",
    ),
    risk_description="There is a 30% probability that the CRM implementation will experience critical technical failures within the first 3 months of deployment.",
    drivers=[
        "Inadequate testing before deployment",
        "Incompatibility with existing systems",
        "Poor data quality in source systems",
    ],
)

# Run the chain
response = get_mitigations_chain(request)

# Access the results
print("Mitigation Measures:")
for mitigation in response.mitigations:
    print(f"- {mitigation}")
```

### Drivers in Presentation Workflow

The driver models are also used in the prepare_presentation_output workflow:

```python
from src.models.schemas import BusinessContext, PresentationRequest, AudienceEnum
from src.workflows import prepare_presentation_output

# Create a request
request = PresentationRequest(
    business_context=BusinessContext(
        project_id="PRJ-2023-001",
        project_description="Implementation of a new CRM system",
        domain_knowledge="The company operates in the B2B sector",
    ),
    audience=AudienceEnum.executive,
    focus_areas=["Technical"],
)

# Run the workflow
response = prepare_presentation_output(request)

# Access the drivers in the response
print("Key Drivers:")
for driver in response.key_drivers:
    print(f"- {driver}")
```