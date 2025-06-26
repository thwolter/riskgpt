# Prioritize Risks

The `prioritize_risks` chain ranks identified risks by urgency or expected impact.

## Input

`PrioritizationRequest`
- `business_context` (`BusinessContext`): project information and language.
- `risks` (`List[str]`): risk descriptions to rank.

## Output

`PrioritizationResponse`
- `prioritized_risks` (`List[str]`): risks ordered by priority.
- `rationale` (`str | None`): explanation of the ranking.
- `response_info` (`ResponseInfo | None`): meta-information including token usage.

## Example

```python
from riskgpt import prioritize_risks_chain
from riskgpt.models.common import BusinessContext
from riskgpt.models.chains import PrioritizationRequest

request = PrioritizationRequest(
    business_context=BusinessContext(
        project_id="ACME-CRM-2023",
        project_name="ACME Corp CRM Implementation",
        project_description="An IT project to introduce a new CRM system across all customer-facing departments",
        language="de",
    ),
    risks=[
        "Datenverlust während der Migration könnte zu Kundenbeziehungsproblemen führen",
        "Systemintegrationsprobleme mit bestehenden ERP-Systemen könnten Verzögerungen verursachen",
        "Mangelnde Benutzerakzeptanz könnte die Effektivität des Systems beeinträchtigen",
        "Budgetüberschreitungen durch unvorhergesehene technische Herausforderungen sind möglich",
        "Datenschutzprobleme könnten zu rechtlichen Konsequenzen führen"
    ],
)

response = prioritize_risks_chain(request)
print("Prioritized Risks:")
for i, risk in enumerate(response.prioritized_risks, 1):
    print(f"{i}. {risk}")
print(f"\nRationale: {response.rationale}")
```
