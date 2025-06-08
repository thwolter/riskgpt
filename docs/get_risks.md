# Get Risks

The `get_risks` chain identifies specific risks for a given risk category.

## Input

`RiskRequest`
- `project_id` (`str`): unique identifier of the project.
- `project_description` (`str`): description of the project.
- `category` (`str`): the risk category to analyse.
- `max_risks` (`int`, optional, default `5`): maximum number of risks to return.
- `domain_knowledge` (`str`, optional): additional domain-specific context.
- `existing_risks` (`List[str]`, optional): already identified risks to exclude.
- `language` (`str`, optional, default `"en"`): language for the response.

## Output

`RiskResponse`
- `risks` (`List[Risk]`): list of identified risks with title, description and category.
- `references` (`List[str] | None`): list of references backing the risks.
- `response_info` (`ResponseInfo | None`): meta-information including token usage.

## Example

```python
from riskgpt.chains.get_risks import get_risks_chain
from riskgpt.models.schemas import RiskRequest

request = RiskRequest(
    project_id="123",
    project_description="An IT project to introduce a new CRM system.",
    category="Technical",
    max_risks=5,
    domain_knowledge="The company operates in the B2B market.",
    existing_risks=["Data loss"],
    language="de"
)

response = get_risks_chain(request)
print(response.risks)
```
