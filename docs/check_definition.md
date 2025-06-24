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
from src.chains.check_definition import check_definition_chain
from src.models.schemas import BusinessContext, DefinitionCheckRequest

request = DefinitionCheckRequest(
    business_context=BusinessContext(
        project_id="123",
        language="de",
    ),
    risk_description="Systemausfall durch mangelnde Wartung kann zu Produktionsstopps führen.",
)

response = check_definition_chain(request)
print(response.revised_description)
```
