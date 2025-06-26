# Context Quality Schema Models

This page documents the schema models related to context quality evaluation in the RiskGPT application.

## Overview

The context quality schema models define the structure for evaluating the quality of the provided project context knowledge. These models are used in the check_context_quality workflow.

## Models

### ContextQualityRequest

```python
class ContextQualityRequest(BaseModel):
    business_context: BusinessContext
    project_type: Optional[str] = None
```

Input model for evaluating context knowledge.

**Fields:**
- `business_context` (BusinessContext): Business context information
- `project_type` (Optional[str]): Type of project for more specific evaluation

**Example:**
```python
{
    "business_context": {
        "project_id": "CRM-2023",
        "project_description": "Implementation of a new CRM system",
        "domain_knowledge": "The company operates in the B2B sector",
        "language": "en",
    },
    "project_type": "IT Implementation",
}
```

### ContextQualityResponse

```python
class ContextQualityResponse(BaseModel):
    shortcomings: List[str]
    rationale: str
    suggested_improvements: str
    response_info: Optional[ResponseInfo] = None
```

Output model describing context quality.

**Fields:**
- `shortcomings` (List[str]): List of identified shortcomings in the context
- `rationale` (str): Explanation for the identified shortcomings
- `suggested_improvements` (str): Suggestions for improving the context
- `response_info` (Optional[ResponseInfo]): Information about the response processing

**Example:**
```python
{
    "shortcomings": [
        "Missing information about existing systems",
        "No details about user base and their technical proficiency",
        "Lack of timeline and budget constraints",
        "No mention of regulatory requirements",
    ],
    "rationale": "The provided context lacks critical information needed for a comprehensive risk assessment of a CRM implementation project. Information about existing systems is essential for identifying integration risks, while understanding the user base helps assess adoption risks.",
    "suggested_improvements": "Enhance the context by adding details about existing systems that will integrate with the new CRM, describe the user base and their technical proficiency, specify timeline and budget constraints, and outline any regulatory requirements that may impact the implementation.",
    "response_info": {
        "consumed_tokens": 1150,
        "total_cost": 0.023,
        "prompt_name": "check_context_quality",
        "model_name": "gpt-4",
    },
}
```

## Usage

These models are used in the check_context_quality workflow to evaluate the quality of the provided project context knowledge and suggest improvements.

### Context Quality Check

```python
from src import BusinessContext, ContextQualityRequest
from src import check_context_quality

# Create a request
request = ContextQualityRequest(
    business_context=BusinessContext(
        project_id="PRJ-2023-001",
        project_description="Implementation of a new CRM system",
        domain_knowledge="The company operates in the B2B sector",
    ),
    project_type="IT Implementation",
)

# Run the workflow
response = check_context_quality(request)

# Access the results
print("Context Quality Evaluation:")
print("\nShortcomings:")
for shortcoming in response.shortcomings:
    print(f"- {shortcoming}")

print(f"\nRationale: {response.rationale}")
print(f"\nSuggested Improvements: {response.suggested_improvements}")
```

### Improving Context Before Risk Analysis

The context quality check can be used to improve the business context before performing risk analysis:

```python
from src import BusinessContext, ContextQualityRequest, RiskRequest
from src import check_context_quality, risk_workflow

# First, check the context quality
initial_context = BusinessContext(
    project_id="PRJ-2023-001",
    project_description="Implementation of a new CRM system",
    domain_knowledge="The company operates in the B2B sector",
)

quality_request = ContextQualityRequest(
    business_context=initial_context,
    project_type="IT Implementation",
)
quality_response = check_context_quality(quality_request)

# Display the suggested improvements
print("Suggested Improvements:")
print(quality_response.suggested_improvements)

# Enhance the context based on the suggestions
# (In a real application, this would involve user input)
enhanced_context = BusinessContext(
    project_id=initial_context.project_id,
    project_description=initial_context.project_description,
    domain_knowledge=f"{initial_context.domain_knowledge}. The system will integrate with existing ERP and billing systems. Users have varying levels of technical proficiency. The project has a 6-month timeline and a budget of $500,000. The company must comply with GDPR and industry-specific regulations.",
)

# Now perform risk analysis with the enhanced context
risk_request = RiskRequest(
    business_context=enhanced_context,
    category="Technical",
)
risk_response = risk_workflow(risk_request)

# The risk analysis will now be more comprehensive due to the improved context
```

### Integration with Other Workflows

The context quality check can be integrated with other workflows to ensure high-quality input:

```python
from src import BusinessContext, ContextQualityRequest, PresentationRequest, AudienceEnum
from src import check_context_quality, prepare_presentation_output

# Check context quality first
context = BusinessContext(
    project_id="PRJ-2023-001",
    project_description="Implementation of a new CRM system",
    domain_knowledge="The company operates in the B2B sector",
)

quality_request = ContextQualityRequest(
    business_context=context,
)
quality_response = check_context_quality(quality_request)

# If there are significant shortcomings, enhance the context
if len(quality_response.shortcomings) > 2:
    print("Please enhance the context with the following improvements:")
    print(quality_response.suggested_improvements)
    # In a real application, get user input to enhance the context
    # For this example, we'll proceed with the original context

# Proceed with the presentation workflow
presentation_request = PresentationRequest(
    business_context=context,
    audience=AudienceEnum.executive,
)
presentation_response = prepare_presentation_output(presentation_request)
```