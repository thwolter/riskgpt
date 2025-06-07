# Get Drivers

The `get_drivers` chain identifies key drivers that influence a specific risk.

## Input

`DriverRequest`
- `project_id` (`str`): unique identifier of the project.
- `risk_description` (`str`): description of the risk.
- `domain_knowledge` (`str`, optional): additional domain-specific context.
- `language` (`str`, optional, default `"en"`): language for the response.

## Output

`DriverResponse`
- `drivers` (`List[str]`): list of identified risk drivers.
- `references` (`List[str] | None`): supporting references in Harvard style.
- `response_info` (`ResponseInfo | None`): meta-information including token usage.

## Example

```python
from riskgpt.chains.get_drivers import get_drivers_chain
from riskgpt.models.schemas import DriverRequest

request = DriverRequest(
    project_id="123",
    risk_description="Systemausfall durch mangelnde Wartung kann zu Produktionsstopps führen.",
    language="de"
)

response = get_drivers_chain(request)
print(response.drivers)
```
