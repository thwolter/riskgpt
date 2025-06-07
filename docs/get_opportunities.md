# Get Opportunities

The `get_opportunities` chain identifies potential positive developments based on known risks.

## Input

`OpportunityRequest`
- `project_id` (`str`): unique identifier of the project.
- `risks` (`List[str]`): list of risks to analyse for opportunities.
- `domain_knowledge` (`str`, optional): additional domain-specific context.
- `language` (`str`, optional, default `"en"`): language for the response.

## Output

`OpportunityResponse`
- `opportunities` (`List[str]`): identified opportunities.
- `references` (`List[str] | None`): supporting references.
- `response_info` (`ResponseInfo | None`): meta-information including token usage.

## Example

```python
from riskgpt.chains.get_opportunities import get_opportunities_chain
from riskgpt.models.schemas import OpportunityRequest

request = OpportunityRequest(
    project_id="123",
    risks=["Systemausfall", "Lieferverzögerung"],
    language="de"
)

response = get_opportunities_chain(request)
print(response.opportunities)
```
