# Get Categories

The `get_categories` chain identifies relevant risk categories for a project description using a language model.

## Input

`CategoryRequest`
- `business_context` (`BusinessContext`): project description, language and other context.
- `existing_categories` (`List[str]`, optional): predefined categories to extend.

## Output

`CategoryResponse`
- `categories` (`List[str]`): list of detected risk categories.
- `rationale` (`str | None`): explanation of the categories.
- `response_info` (`ResponseInfo | None`): meta-information including token usage.

## Example

```python
from src import risk_categories_chain
from src import BusinessContext, CategoryRequest

request = CategoryRequest(
    business_context=BusinessContext(
        project_id="123",
        project_description="An IT project to introduce a new CRM system.",
        domain_knowledge="The company operates in the B2B market.",
        language="de",
    ),
    existing_categories=["technical", "strategic"],
)

response = risk_categories_chain(request)
print(response.categories)
```
