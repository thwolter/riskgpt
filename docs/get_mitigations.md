# Get Mitigations

The `get_mitigations` chain suggests mitigation measures for a risk based on its drivers.
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
from src import risk_mitigations_chain
from src import BusinessContext, MitigationRequest

request = MitigationRequest(
    business_context=BusinessContext(
        project_id="123",
        language="de",
    ),
    risk_description="Systemausfall durch mangelnde Wartung kann zu Produktionsstopps führen.",
    drivers=["veraltete Hardware"],
)

response = risk_mitigations_chain(request)
print(response.mitigations)
```
