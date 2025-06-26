# Presentation Schema Models

This page documents the schema models related to presentation output in the RiskGPT application.

## Overview

The presentation schema models define the structure for creating presentation-ready summaries tailored to different audiences. These models are used in the prepare_presentation_output workflow.

## Models

### AudienceEnum

```python
class AudienceEnum(str, Enum):
    executive = "executive"
    workshop = "workshop"
    risk_internal = "risk_internal"
    audit = "audit"
    regulator = "regulator"
    project_owner = "project_owner"
    investor = "investor"
    operations = "operations"
```

Supported audiences for presentation output.

**Values:**
- `executive`: For executive leadership
- `workshop`: For risk workshop participants
- `risk_internal`: For internal risk management teams
- `audit`: For audit teams
- `regulator`: For regulatory bodies
- `project_owner`: For project owners and managers
- `investor`: For investors and stakeholders
- `operations`: For operations teams

### PresentationRequest

```python
class PresentationRequest(BaseModel):
    business_context: BusinessContext
    audience: AudienceEnum
    focus_areas: Optional[List[str]] = None
```

Input model for presentation-oriented summaries.

**Fields:**
- `business_context` (BusinessContext): Business context information
- `audience` (AudienceEnum): Target audience for the presentation
- `focus_areas` (Optional[List[str]]): Specific areas to focus on

**Example:**
```python
{
    "business_context": {
        "project_id": "CRM-2023",
        "project_description": "Implementation of a new CRM system",
        "language": "en",
    },
    "audience": "executive",
    "focus_areas": ["Technical", "Organizational"],
}
```

### PresentationResponse

```python
class PresentationResponse(BaseModel):
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
```

Structured output for presentation-ready summaries.

**Fields:**
- `executive_summary` (str): High-level summary for executives
- `main_risks` (List[str]): List of main risks identified
- `quantitative_summary` (Optional[str]): Quantitative assessment summary
- `key_drivers` (Optional[List[str]]): List of key risk drivers
- `correlation_tags` (Optional[List[str]]): Tags for correlation analysis
- `mitigations` (Optional[List[str]]): List of mitigation measures
- `open_questions` (Optional[List[str]]): Questions for discussion
- `chart_placeholders` (Optional[List[str]]): Placeholders for charts
- `appendix` (Optional[str]): Additional information
- `response_info` (Optional[ResponseInfo]): Information about the response processing

**Example:**
```python
{
    "executive_summary": "The CRM implementation project faces several significant risks that require attention. The most critical risks are related to data migration, user adoption, and system integration.",
    "main_risks": [
        "Data Migration Failure",
        "User Adoption Issues",
        "Integration Problems",
    ],
    "quantitative_summary": "Data Migration Failure: P=0.3, I=0.7\nUser Adoption Issues: P=0.5, I=0.4\nIntegration Problems: P=0.2, I=0.6",
    "key_drivers": [
        "Inadequate testing",
        "Resistance to change",
        "Technical complexity",
    ],
    "correlation_tags": [
        "technical_complexity",
        "change_management",
        "data_quality",
    ],
    "mitigations": [
        "Implement comprehensive testing plan",
        "Develop change management strategy",
        "Conduct data quality assessment",
    ],
    "open_questions": [
        "What is the timeline for user training?",
        "Has a data backup strategy been established?",
    ],
    "chart_placeholders": [
        "risk_overview_chart",
    ],
    "appendix": "Technical details of risk assessment methodology",
    "response_info": {
        "consumed_tokens": 2500,
        "total_cost": 0.05,
        "prompt_name": "prepare_presentation_output",
        "model_name": "gpt-4",
    },
}
```

### CommunicationRequest

```python
class CommunicationRequest(BaseModel):
    business_context: BusinessContext
    summary: str
```

Input for summarising risks for stakeholders.

**Fields:**
- `business_context` (BusinessContext): Business context information
- `summary` (str): Risk summary to communicate

**Example:**
```python
{
    "business_context": {
        "project_id": "CRM-2023",
        "project_description": "Implementation of a new CRM system",
        "language": "en",
    },
    "summary": "Data Migration Failure: P=0.3, I=0.7\nUser Adoption Issues: P=0.5, I=0.4\nIntegration Problems: P=0.2, I=0.6",
}
```

### CommunicationResponse

```python
class CommunicationResponse(BaseModel):
    executive_summary: str
    technical_annex: Optional[str] = None
    response_info: Optional[ResponseInfo] = None
```

Output model for risk communication.

**Fields:**
- `executive_summary` (str): High-level summary for executives
- `technical_annex` (Optional[str]): Technical details for specialists
- `response_info` (Optional[ResponseInfo]): Information about the response processing

**Example:**
```python
{
    "executive_summary": "The CRM implementation project faces several significant risks that require attention. The most critical risks are related to data migration, user adoption, and system integration.",
    "technical_annex": "Detailed risk assessment results:\n- Data Migration Failure: Probability 30%, Impact 70%\n- User Adoption Issues: Probability 50%, Impact 40%\n- Integration Problems: Probability 20%, Impact 60%",
    "response_info": {
        "consumed_tokens": 1200,
        "total_cost": 0.024,
        "prompt_name": "communicate_risks",
        "model_name": "gpt-4",
    },
}
```

## Usage

These models are used in the prepare_presentation_output workflow to create presentation-ready summaries tailored to different audiences.

### Presentation Output

```python
from src import BusinessContext, PresentationRequest, AudienceEnum
from src import prepare_presentation_output

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

# Access the results
print(f"Executive Summary: {response.executive_summary}")
print("\nMain Risks:")
for risk in response.main_risks:
    print(f"- {risk}")

if response.key_drivers:
    print("\nKey Drivers:")
    for driver in response.key_drivers:
        print(f"- {driver}")

if response.mitigations:
    print("\nMitigations:")
    for mitigation in response.mitigations:
        print(f"- {mitigation}")
```

### Different Audiences

The output is automatically adjusted based on the target audience:

```python
# For executive audience
executive_request = PresentationRequest(
    business_context=BusinessContext(
        project_id="PRJ-2023-001",
        project_description="Implementation of a new CRM system",
    ),
    audience=AudienceEnum.executive,
)
executive_response = prepare_presentation_output(executive_request)
# Executive output has top 3 risks, executive overview chart, no open questions

# For workshop audience
workshop_request = PresentationRequest(
    business_context=BusinessContext(
        project_id="PRJ-2023-001",
        project_description="Implementation of a new CRM system",
    ),
    audience=AudienceEnum.workshop,
)
workshop_response = prepare_presentation_output(workshop_request)
# Workshop output includes open questions for discussion

# For risk internal audience
risk_internal_request = PresentationRequest(
    business_context=BusinessContext(
        project_id="PRJ-2023-001",
        project_description="Implementation of a new CRM system",
    ),
    audience=AudienceEnum.risk_internal,
)
risk_internal_response = prepare_presentation_output(risk_internal_request)
# Risk internal output includes model parameters in appendix
```

### Risk Communication

The communication models can be used directly:

```python
from src import BusinessContext, CommunicationRequest
from src import communicate_risks_chain

# Create a request
request = CommunicationRequest(
    business_context=BusinessContext(
        project_id="PRJ-2023-001",
        project_description="Implementation of a new CRM system",
    ),
    summary="Data Migration Failure: P=0.3, I=0.7\nUser Adoption Issues: P=0.5, I=0.4\nIntegration Problems: P=0.2, I=0.6",
)

# Run the chain
response = communicate_risks_chain(request)

# Access the results
print(f"Executive Summary: {response.executive_summary}")
if response.technical_annex:
    print(f"\nTechnical Annex: {response.technical_annex}")
```