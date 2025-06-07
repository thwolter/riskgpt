# Get Mitigations

The `get_mitigations` chain suggests mitigation measures for a risk based on its drivers.

## Input

`MitigationRequest`
- `project_id` (`str`): unique identifier of the project.
- `risk_description` (`str`): description of the risk.
- `drivers` (`List[str]`, optional): identified drivers for this risk.
- `domain_knowledge` (`str`, optional): additional domain-specific context.
- `language` (`str`, optional, default `"en"`): language for the response.

## Output

`MitigationResponse`
- `mitigations` (`List[str]`): proposed mitigation measures.
- `references` (`List[str] | None`): supporting references.
- `response_info` (`ResponseInfo | None`): meta-information including token usage.

## Example

```python
from riskgpt.chains.get_mitigations import get_mitigations_chain
from riskgpt.models.schemas import MitigationRequest

request = MitigationRequest(
    project_id="123",
    risk_description="Systemausfall durch mangelnde Wartung kann zu Produktionsstopps führen.",
    drivers=["veraltete Hardware"],
    language="de"
)

response = get_mitigations_chain(request)
print(response.mitigations)
```
