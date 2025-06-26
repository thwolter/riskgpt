# Risk Mitigations

The `risk_mitigations_chain` suggests mitigation measures for a risk based on its drivers.
It also includes the system prompt so that references are only given when the model
is reasonably sure of a real source.

## Input

`MitigationRequest`
- `business_context` (`BusinessContext`): project information and language.
- `risk_description` (`str`): description of the risk.
- `drivers` (`List[str]`, optional): identified drivers for this risk.

## Output

`MitigationResponse`
- `mitigations` (`List[str]`): proposed mitigation measures.
- `references` (`List[str] | None`): supporting references.
- `response_info` (`ResponseInfo | None`): meta-information including token usage.

## Example

```python
from riskgpt import risk_mitigations_chain
from riskgpt.models.common import BusinessContext
from riskgpt.models.chains import MitigationRequest

request = MitigationRequest(
    business_context=BusinessContext(
        project_id="ACME-MFG-2023",
        project_name="ACME Manufacturing Plant Upgrade",
        project_description="Modernization of production line equipment and control systems",
        language="de",
    ),
    risk_description="Systemausfall durch mangelnde Wartung kann zu Produktionsstopps führen und erhebliche finanzielle Verluste verursachen.",
    drivers=[
        "Veraltete Hardware mit hoher Ausfallwahrscheinlichkeit",
        "Unzureichende Wartungspläne und -prozesse",
        "Mangel an qualifiziertem Wartungspersonal",
        "Fehlende Ersatzteile für kritische Komponenten"
    ],
)

response = risk_mitigations_chain(request)
print("Mitigation Strategies:")
for i, mitigation in enumerate(response.mitigations, 1):
    print(f"{i}. {mitigation}")
```