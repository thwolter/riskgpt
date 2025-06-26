# Prepare Presentation Output

The `prepare_presentation_output` workflow creates presentation-ready summaries tailored to different audiences, combining risk identification, assessment, drivers, mitigations, and correlation analysis into a comprehensive output.

## Overview

The Prepare Presentation Output workflow combines multiple steps into a single workflow:

1. Risk identification for the specified focus area
2. Risk assessment for each identified risk
3. Driver identification for each risk
4. Mitigation suggestions for each risk
5. Correlation tag generation across all risks
6. Summary generation with audience-specific formatting

This workflow is designed to create presentation-ready outputs for different audiences, including executives, workshop participants, risk teams, auditors, regulators, project owners, investors, and operations teams.

## Usage

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

print(f"\nQuantitative Summary: {response.quantitative_summary}")

print("\nKey Drivers:")
for driver in response.key_drivers:
    print(f"- {driver}")

print("\nCorrelation Tags:")
for tag in response.correlation_tags:
    print(f"- {tag}")

print("\nMitigations:")
for mitigation in response.mitigations:
    print(f"- {mitigation}")

if response.open_questions:
    print("\nOpen Questions:")
    for question in response.open_questions:
        print(f"- {question}")

if response.chart_placeholders:
    print("\nChart Placeholders:")
    for chart in response.chart_placeholders:
        print(f"- {chart}")

if response.appendix:
    print(f"\nAppendix: {response.appendix}")
```

## Audience Customization

The workflow automatically adjusts the output based on the target audience:

- **Executive**: Limits to top 3 risks, includes executive overview chart, removes open questions
- **Workshop**: Includes open questions for discussion
- **Risk Internal**: Adds model parameters to appendix
- **Audit**: Adds audit trail to appendix
- **Regulator**: Adds compliance mapping to appendix
- **Project Owner**: Adds project milestones to appendix
- **Investor**: Adds financial impact to appendix
- **Operations**: Adds KRI dashboard to appendix

```python
# For executive audience
executive_request = PresentationRequest(
    business_context=business_context,
    audience=AudienceEnum.executive,
    focus_areas=["Technical"],
)
executive_response = prepare_presentation_output(executive_request)

# For workshop audience
workshop_request = PresentationRequest(
    business_context=business_context,
    audience=AudienceEnum.workshop,
    focus_areas=["Technical"],
)
workshop_response = prepare_presentation_output(workshop_request)
```

## Input Schema

`PresentationRequest`
- `business_context` (`BusinessContext`): Business context information
- `audience` (`AudienceEnum`): Target audience for the presentation
- `focus_areas` (`List[str]`, optional): Specific areas to focus on

## Output Schema

`PresentationResponse`
- `executive_summary` (`str`): High-level summary for executives
- `main_risks` (`List[str]`): List of main risks identified
- `quantitative_summary` (`str`, optional): Quantitative assessment summary
- `key_drivers` (`List[str]`, optional): List of key risk drivers
- `correlation_tags` (`List[str]`, optional): Tags for correlation analysis
- `mitigations` (`List[str]`, optional): List of mitigation measures
- `open_questions` (`List[str]`, optional): Questions for discussion
- `chart_placeholders` (`List[str]`, optional): Placeholders for charts
- `appendix` (`str`, optional): Additional information
- `response_info` (`ResponseInfo`, optional): Token and cost meta information