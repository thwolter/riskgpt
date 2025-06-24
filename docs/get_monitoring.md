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
from src.chains.risk_indicators import risk_indicators_chain
from src.models.schemas import BusinessContext, MonitoringRequest

request = MonitoringRequest(
    business_context=BusinessContext(
        project_id="123",
        language="de",
    ),
    risk_description="Systemausfall durch mangelnde Wartung",
)

response = risk_indicators_chain(request)
print(response.indicators)
```
