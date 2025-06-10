# Get Monitoring

The `get_monitoring` chain derives indicators for ongoing risk monitoring.

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
from riskgpt.chains.get_monitoring import get_monitoring_chain
from riskgpt.models.schemas import BusinessContext, MonitoringRequest

request = MonitoringRequest(
    business_context=BusinessContext(
        project_id="123",
        language="de",
    ),
    risk_description="Systemausfall durch mangelnde Wartung",
)

response = get_monitoring_chain(request)
print(response.indicators)
```
