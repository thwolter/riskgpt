# Risk Indicators

The `risk_indicators_chain` derives indicators for ongoing risk monitoring.

## Input

`MonitoringRequest`
- `business_context` (`BusinessContext`): project information and language.
- `risk_description` (`str`): description of the risk.

## Output

`MonitoringResponse`
- `indicators` (`List[str]`): monitoring metrics or warning signals.
- `references` (`List[str] | None`): supporting references.
- `response_info` (`ResponseInfo | None`): meta-information including token usage.

## Example

```python
from riskgpt import risk_indicators_chain
from riskgpt.models.common import BusinessContext
from riskgpt.models.chains import MonitoringRequest

request = MonitoringRequest(
    business_context=BusinessContext(
        project_id="ACME-MFG-2023",
        project_name="ACME Manufacturing Plant Upgrade",
        project_description="Modernization of production line equipment and control systems",
        language="de",
    ),
    risk_description="Systemausfall durch mangelnde Wartung kann zu Produktionsstopps führen und erhebliche finanzielle Verluste verursachen.",
)

response = risk_indicators_chain(request)
print("Monitoring Indicators:")
for i, indicator in enumerate(response.indicators, 1):
    print(f"{i}. {indicator}")
```