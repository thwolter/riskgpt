# Cost Benefit

The `cost_benefit` chain estimates the effort or cost of mitigations relative to their expected benefit.

## Input

`CostBenefitRequest`
- `business_context` (`BusinessContext`): project information and language.
- `risk_description` (`str`): description of the risk.
- `mitigations` (`List[str]`): proposed mitigation measures.

## Output

`CostBenefitResponse`
- `analyses` (`List[CostBenefit]`): estimated cost and benefit for each mitigation.
- `references` (`List[str] | None`): supporting references.
- `response_info` (`ResponseInfo | None`): meta-information including token usage.

## Example

```python
from src import cost_benefit_chain
from src import BusinessContext, CostBenefitRequest

request = CostBenefitRequest(
    business_context=BusinessContext(
        project_id="123",
        language="de",
    ),
    risk_description="Systemausfall durch mangelnde Wartung",
    mitigations=["regelmäßige Wartung", "Backup-System"],
)

response = cost_benefit_chain(request)
print(response.analyses)
```
