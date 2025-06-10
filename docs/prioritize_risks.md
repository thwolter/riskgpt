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
from riskgpt.chains.prioritize_risks import prioritize_risks_chain
from riskgpt.models.schemas import BusinessContext, PrioritizationRequest

request = PrioritizationRequest(
    business_context=BusinessContext(
        project_id="123",
        language="de",
    ),
    risks=["Delayed delivery", "Budget overrun"],
)

response = prioritize_risks_chain(request)
print(response.prioritized_risks)
```
