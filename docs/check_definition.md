# Check Definition

The `check_definition` chain validates and revises a risk description so that it follows the event–cause–consequence logic.

## Input

`DefinitionCheckRequest`
- `business_context` (`BusinessContext`): project information and language.
- `risk_description` (`str`): risk definition provided by the user.

## Output

`DefinitionCheckResponse`
- `revised_description` (`str`): risk definition rewritten in the proper format.
- `rationale` (`str | None`): explanation of the changes.
- `response_info` (`ResponseInfo | None`): meta-information including token usage.

## Example

```python
from riskgpt import check_definition_chain
from riskgpt.models.common import BusinessContext
from riskgpt.models.chains import DefinitionCheckRequest

request = DefinitionCheckRequest(
    business_context=BusinessContext(
        project_id="ACME-MFG-2023",
        project_name="ACME Manufacturing Plant Upgrade",
        project_description="Modernization of production line equipment and control systems",
        language="de",
    ),
    risk_description="Systemausfall durch mangelnde Wartung kann zu Produktionsstopps führen.",
)

response = check_definition_chain(request)
print(f"Original: {request.risk_description}")
print(f"Revised: {response.revised_description}")
print(f"Rationale: {response.rationale}")
```
