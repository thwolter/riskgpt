# Risk Drivers

The `risk_drivers_chain` identifies key drivers that influence a specific risk.
It uses the shared system prompt so that any cited evidence should only
reference sources the model is confident actually exist.

## Input

`DriverRequest`
- `business_context` (`BusinessContext`): project information and language.
- `risk_description` (`str`): description of the risk.

## Output

`DriverResponse`
- `drivers` (`List[str]`): list of identified risk drivers.
- `references` (`List[str] | None`): supporting references in Harvard style.
- `response_info` (`ResponseInfo | None`): meta-information including token usage.

## Example

```python
from riskgpt import risk_drivers_chain
from riskgpt.models.common import BusinessContext
from riskgpt.models.chains import DriverRequest

request = DriverRequest(
    business_context=BusinessContext(
        project_id="ACME-MFG-2023",
        project_name="ACME Manufacturing Plant Upgrade",
        project_description="Modernization of production line equipment and control systems",
        language="de",
    ),
    risk_description="Systemausfall durch mangelnde Wartung kann zu Produktionsstopps führen und erhebliche finanzielle Verluste verursachen.",
)

response = risk_drivers_chain(request)
print("Risk Drivers:")
for i, driver in enumerate(response.drivers, 1):
    print(f"{i}. {driver}")
```