# Get Risks

The `get_risks` chain identifies specific risks for a given risk category.

## Input

`RiskRequest`
- `business_context` (`BusinessContext`): project description, language and other context.
- `category` (`str`): the risk category to analyse.
- `max_risks` (`int`, optional, default `5`): maximum number of risks to return.
- `existing_risks` (`List[str]`, optional): already identified risks to exclude.
- `document_refs` (`List[str]`, optional): document IDs from the microservice.

## Output

`RiskResponse`
- `risks` (`List[Risk]`): list of identified risks with title, description and category.
- `references` (`List[str] | None`): list of references backing the risks.
- `response_info` (`ResponseInfo | None`): meta-information including token usage.

## Example

```python
from src.chains.risk_identification import risk_identification_chain
from src.models.schemas import BusinessContext, RiskRequest

request = RiskRequest(
    business_context=BusinessContext(
        project_id="123",
        project_description="An IT project to introduce a new CRM system.",
        domain_knowledge="The company operates in the B2B market.",
        language="de",
    ),
    category="Technical",
    max_risks=5,
    existing_risks=["Data loss"],
)

response = risk_identification_chain(request)
print(response.risks)
```
