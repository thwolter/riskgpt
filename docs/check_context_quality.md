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
from src.workflows import check_context_quality
from src.models.schemas import ContextQualityRequest

req = ContextQualityRequest(
    context_knowledge="We plan to update our CRM system.",
    project_type="IT",
)
resp = check_context_quality(req)
print(resp.shortcomings)
```
