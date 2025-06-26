# Get Drivers

The `get_drivers` chain identifies key drivers that influence a specific risk.
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
from src import risk_drivers_chain
from src import BusinessContext, DriverRequest

request = DriverRequest(
    business_context=BusinessContext(
        project_id="123",
        language="de",
    ),
    risk_description="Systemausfall durch mangelnde Wartung kann zu Produktionsstopps führen.",
)

response = risk_drivers_chain(request)
print(response.drivers)
```
