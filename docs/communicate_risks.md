# Communicate Risks

The `communicate_risks` chain generates concise summaries or slide text for stakeholders.

## Input

`CommunicationRequest`
- `project_id` (`str`): unique identifier of the project.
- `summary` (`str`): text to summarise.
- `domain_knowledge` (`str`, optional): additional domain-specific context.
- `language` (`str`, optional, default `"en"`): language for the response.

## Output

`CommunicationResponse`
- `report` (`str`): generated communication text.
- `response_info` (`ResponseInfo | None`): meta-information including token usage.

## Example

```python
from riskgpt.chains.communicate_risks import communicate_risks_chain
from riskgpt.models.schemas import CommunicationRequest

request = CommunicationRequest(
    project_id="123",
    summary="Key CRM project risks were identified and assessed.",
    language="de"
)

response = communicate_risks_chain(request)
print(response.report)
```
