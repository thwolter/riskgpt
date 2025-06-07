# Get Monitoring

The `get_monitoring` chain derives indicators for ongoing risk monitoring.

## Input

`MonitoringRequest`
- `project_id` (`str`): unique identifier of the project.
- `risk_description` (`str`): description of the risk.
- `domain_knowledge` (`str`, optional): additional domain-specific context.
- `language` (`str`, optional, default `"en"`): language for the response.

## Output

`MonitoringResponse`
- `indicators` (`List[str]`): monitoring metrics or warning signals.
- `references` (`List[str] | None`): supporting references.
- `response_info` (`ResponseInfo | None`): meta-information including token usage.

## Example

```python
from riskgpt.chains.get_monitoring import get_monitoring_chain
from riskgpt.models.schemas import MonitoringRequest

request = MonitoringRequest(
    project_id="123",
    risk_description="Systemausfall durch mangelnde Wartung",
    language="de"
)

response = get_monitoring_chain(request)
print(response.indicators)
```
