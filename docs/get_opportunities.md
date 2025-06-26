# Get Opportunities

The `get_opportunities` chain identifies potential positive developments based on known risks.

## Input

`OpportunityRequest`
- `business_context` (`BusinessContext`): project information and language.
- `risks` (`List[str]`): list of risks to analyse for opportunities.

## Output

`OpportunityResponse`
- `opportunities` (`List[str]`): identified opportunities.
- `references` (`List[str] | None`): supporting references.
- `response_info` (`ResponseInfo | None`): meta-information including token usage.

## Example

```python
from src import opportunities_chain
from src import BusinessContext, OpportunityRequest

request = OpportunityRequest(
    business_context=BusinessContext(
        project_id="123",
        language="de",
    ),
    risks=["Systemausfall", "Lieferverzögerung"],
)

response = opportunities_chain(request)
print(response.opportunities)
```
