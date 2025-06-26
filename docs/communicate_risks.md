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
from src import communicate_risks_chain
from src import BusinessContext, CommunicationRequest

request = CommunicationRequest(
    business_context=BusinessContext(
        project_id="123",
        language="de",
    ),
    summary="Key CRM project risks were identified and assessed."
)

response = communicate_risks_chain(request)
print(response.report)
```
