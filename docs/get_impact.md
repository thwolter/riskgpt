# Get Impact

The `get_impact` chain estimates the potential impact of a risk using a three-point estimate and suggests a probability distribution.

## Input

`ImpactRequest`
- `project_id` (`str`): unique identifier of the project.
- `risk_description` (`str`): description of the risk.
- `domain_knowledge` (`str`, optional): additional domain-specific context.
- `language` (`str`, optional, default `"en"`): language for the response.

## Output

`ImpactResponse`
- `minimum` (`float`): lower bound of the impact estimate.
- `most_likely` (`float`): most likely impact value.
- `maximum` (`float`): upper bound of the impact estimate.
- `distribution` (`str`): suggested probability distribution.
- `references` (`List[str] | None`): supporting references.
- `response_info` (`ResponseInfo | None`): meta-information including token usage.

## Example

```python
from riskgpt.chains.get_impact import get_impact_chain
from riskgpt.models.schemas import ImpactRequest

request = ImpactRequest(
    project_id="123",
    risk_description="Systemausfall durch mangelnde Wartung kann zu Produktionsstopps führen.",
    language="de"
)

response = get_impact_chain(request)
print(response.most_likely)
```
