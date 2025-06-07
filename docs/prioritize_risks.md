# Prioritize Risks

The `prioritize_risks` chain ranks identified risks by urgency or expected impact.

## Input

`PrioritizationRequest`
- `project_id` (`str`): unique identifier of the project.
- `risks` (`List[str]`): risk descriptions to rank.
- `domain_knowledge` (`str`, optional): additional domain-specific context.
- `language` (`str`, optional, default `"en"`): language for the response.

## Output

`PrioritizationResponse`
- `prioritized_risks` (`List[str]`): risks ordered by priority.
- `rationale` (`str | None`): explanation of the ranking.
- `response_info` (`ResponseInfo | None`): meta-information including token usage.

## Example

```python
from riskgpt.chains.prioritize_risks import prioritize_risks_chain
from riskgpt.models.schemas import PrioritizationRequest

request = PrioritizationRequest(
    project_id="123",
    risks=["Delayed delivery", "Budget overrun"],
    language="de"
)

response = prioritize_risks_chain(request)
print(response.prioritized_risks)
```
