# Get Categories

The `get_categories` chain identifies relevant risk categories for a project description using a language model.

## Input

`CategoryRequest`
- `project_id` (`str`): unique identifier of the project.
- `project_description` (`str`): description of the project.
- `domain_knowledge` (`str`, optional): additional domain-specific context.
- `language` (`str`, optional, default `"en"`): language for the response.

## Output

`CategoryResponse`
- `categories` (`List[str]`): list of detected risk categories.
- `rationale` (`str | None`): explanation of the categories.
- `response_info` (`ResponseInfo | None`): meta-information including token usage.

## Example

```python
from riskgpt.chains.get_categories import get_categories_chain
from riskgpt.models.schemas import CategoryRequest

request = CategoryRequest(
    project_id="123",
    project_description="An IT project to introduce a new CRM system.",
    domain_knowledge="The company operates in the B2B market.",
    language="de"
)

response = get_categories_chain(request)
print(response.categories)
```
