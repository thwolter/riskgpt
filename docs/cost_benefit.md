# Cost Benefit

The `cost_benefit` chain estimates the effort or cost of mitigations relative to their expected benefit.

## Input

`CostBenefitRequest`
- `project_id` (`str`): unique identifier of the project.
- `risk_description` (`str`): description of the risk.
- `mitigations` (`List[str]`): proposed mitigation measures.
- `domain_knowledge` (`str`, optional): additional domain-specific context.
- `language` (`str`, optional, default `"en"`): language for the response.

## Output

`CostBenefitResponse`
- `analyses` (`List[CostBenefit]`): estimated cost and benefit for each mitigation.
- `references` (`List[str] | None`): supporting references.
- `response_info` (`ResponseInfo | None`): meta-information including token usage.

## Example

```python
from riskgpt.chains.cost_benefit import cost_benefit_chain
from riskgpt.models.schemas import CostBenefitRequest

request = CostBenefitRequest(
    project_id="123",
    risk_description="Systemausfall durch mangelnde Wartung",
    mitigations=["regelmäßige Wartung", "Backup-System"],
    language="de"
)

response = cost_benefit_chain(request)
print(response.analyses)
```
