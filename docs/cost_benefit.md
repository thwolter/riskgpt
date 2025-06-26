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
from riskgpt import cost_benefit_chain
from riskgpt.models.common import BusinessContext
from riskgpt.models.chains import CostBenefitRequest

request = CostBenefitRequest(
    business_context=BusinessContext(
        project_id="ACME-MFG-2023",
        project_name="ACME Manufacturing Plant Upgrade",
        project_description="Modernization of production line equipment and control systems",
        language="de",
    ),
    risk_description="Systemausfall durch mangelnde Wartung kann zu Produktionsstopps führen und erhebliche finanzielle Verluste verursachen.",
    mitigations=[
        "Implementierung eines präventiven Wartungsplans mit regelmäßigen Inspektionen",
        "Installation eines redundanten Backup-Systems für kritische Komponenten",
        "Schulung des Personals zur Früherkennung von Systemausfällen",
        "Einrichtung eines Notfallplans für schnelle Wiederherstellung im Falle eines Ausfalls"
    ],
)

response = cost_benefit_chain(request)
print("Cost-Benefit Analysis:")
for i, analysis in enumerate(response.analyses, 1):
    print(f"{i}. Mitigation: {analysis.mitigation}")
    print(f"   Cost: {analysis.cost}")
    print(f"   Benefit: {analysis.benefit}")
    print(f"   Ratio: {analysis.ratio}")
```
