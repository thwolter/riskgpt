# Check Definition

The `check_definition` chain validates and revises a risk description so that it follows the event–cause–consequence logic.

## Input

`DefinitionCheckRequest`
- `project_id` (`str`): unique identifier of the project.
- `risk_description` (`str`): risk definition provided by the user.
- `domain_knowledge` (`str`, optional): additional domain-specific context.
- `language` (`str`, optional, default `"en"`): language for the response.

## Output

`DefinitionCheckResponse`
- `revised_description` (`str`): risk definition rewritten in the proper format.
- `rationale` (`str | None`): explanation of the changes.
- `response_info` (`ResponseInfo | None`): meta-information including token usage.

## Example

```python
from riskgpt.chains.check_definition import check_definition_chain
from riskgpt.models.schemas import DefinitionCheckRequest

request = DefinitionCheckRequest(
    project_id="123",
    risk_description="Systemausfall durch mangelnde Wartung kann zu Produktionsstopps führen.",
    language="de"
)

response = check_definition_chain(request)
print(response.revised_description)
```
