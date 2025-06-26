# Check Context Quality

The `check_context_quality` workflow evaluates whether the provided context information is detailed enough for subsequent risk, opportunity and impact analysis.

## Input

`ContextQualityRequest`
- `context_knowledge` (`str`): text description of the project context.
- `project_type` (`str`, optional): domain or project type for tailored feedback.
- `language` (`str`, optional, default `"en"`): language for the response.

## Output

`ContextQualityResponse`
- `shortcomings` (`List[str]`): bullet list of missing or weak aspects.
- `rationale` (`str`): short explanation with at least one Harvard style citation.
- `suggested_improvements` (`str`): revised context text.
- `response_info` (`ResponseInfo | None`): token and cost meta information.

## Example

```python
from riskgpt import check_context_quality
from riskgpt.models.workflows.context_quality import ContextQualityRequest

req = ContextQualityRequest(
    context_knowledge="""
    ACME Corp plans to update our CRM system from the current legacy platform to a cloud-based solution. 
    The project will affect our sales and customer service departments. 
    We have approximately 500 users who will need to be migrated to the new system.
    """,
    project_type="IT Infrastructure",
    language="en"
)

resp = check_context_quality(req)

print("Context Quality Assessment:")
print("\nShortcomings:")
for i, shortcoming in enumerate(resp.shortcomings, 1):
    print(f"{i}. {shortcoming}")

print("\nRationale:")
print(resp.rationale)

print("\nSuggested Improvements:")
print(resp.suggested_improvements)
```
