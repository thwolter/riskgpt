# Communicate Risks

The `communicate_risks` chain generates concise summaries or slide text for stakeholders.

## Input

`CommunicationRequest`
- `business_context` (`BusinessContext`): project information and language.
- `summary` (`str`): text to summarise.

## Output

`CommunicationResponse`
- `report` (`str`): generated communication text.
- `response_info` (`ResponseInfo | None`): meta-information including token usage.

## Example

```python
from riskgpt import communicate_risks_chain
from riskgpt.models.common import BusinessContext
from riskgpt.models.chains import CommunicationRequest

request = CommunicationRequest(
    business_context=BusinessContext(
        project_id="ACME-CRM-2023",
        project_name="ACME Corp CRM Implementation",
        project_description="An IT project to introduce a new CRM system across all customer-facing departments",
        audience="executive",
        language="de",
    ),
    summary="""
    Die Implementierung des neuen CRM-Systems birgt mehrere Risiken:
    1. Datenverlust während der Migration könnte zu Kundenbeziehungsproblemen führen
    2. Systemintegrationsprobleme mit bestehenden ERP-Systemen könnten Verzögerungen verursachen
    3. Mangelnde Benutzerakzeptanz könnte die Effektivität des Systems beeinträchtigen
    4. Budgetüberschreitungen durch unvorhergesehene technische Herausforderungen sind möglich
    """
)

response = communicate_risks_chain(request)
print("Executive Summary:")
print(response.report)
```
