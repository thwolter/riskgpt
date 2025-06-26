# Opportunities

The `opportunities_chain` identifies potential positive developments based on known risks.

## Input

`OpportunityRequest`
- `business_context` (`BusinessContext`): project information and language.
- `risks` (`List[str]`): list of risks to analyze for opportunities.

## Output

`OpportunityResponse`
- `opportunities` (`List[str]`): identified opportunities.
- `references` (`List[str] | None`): supporting references.
- `response_info` (`ResponseInfo | None`): meta-information including token usage.

## Example

```python
from riskgpt import opportunities_chain
from riskgpt.models.common import BusinessContext
from riskgpt.models.chains import OpportunityRequest

request = OpportunityRequest(
    business_context=BusinessContext(
        project_id="ACME-CYB-2023",
        project_name="ACME Corp Cybersecurity Upgrade",
        project_description="Implementation of enhanced cybersecurity measures across all departments",
        language="de",
    ),
    risks=[
        "Systemausfall während der Implementierung",
        "Verzögerung bei der Schulung der Mitarbeiter",
        "Inkompatibilität mit bestehenden Systemen"
    ],
)

response = opportunities_chain(request)
print(response.opportunities)
```