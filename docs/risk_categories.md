# Risk Categories

The `risk_categories_chain` identifies relevant risk categories for a project description using a language model.

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
from riskgpt import risk_categories_chain
from riskgpt.models.common import BusinessContext
from riskgpt.models.chains import CategoryRequest

request = CategoryRequest(
    business_context=BusinessContext(
        project_id="ACME-CRM-2023",
        project_name="ACME Corp CRM Implementation",
        project_description="An IT project to introduce a new CRM system across all customer-facing departments to improve customer relationship management and sales tracking.",
        domain_knowledge="The company operates in the B2B market with a focus on manufacturing equipment for the automotive industry.",
        language="de",
    ),
    existing_categories=["technical", "strategic"],
)

response = risk_categories_chain(request)
print(response.categories)
```