# Risk Identification

The `risk_identification_chain` identifies specific risks for a given risk category.

## Input

`RiskRequest`
- `business_context` (`BusinessContext`): project description, language and other context.
- `category` (`str`): the risk category to analyze.
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
from riskgpt import risk_identification_chain
from riskgpt.models.common import BusinessContext
from riskgpt.models.chains import RiskRequest

request = RiskRequest(
    business_context=BusinessContext(
        project_id="ACME-CRM-2023",
        project_name="ACME Corp CRM Implementation",
        project_description="An IT project to introduce a new CRM system across all customer-facing departments to improve customer relationship management and sales tracking.",
        domain_knowledge="The company operates in the B2B market with a focus on manufacturing equipment for the automotive industry.",
        language="de",
    ),
    category="Technical",
    max_risks=5,
    existing_risks=["Datenverlust während der Migration"],
    document_refs=["doc-technical-requirements", "doc-system-architecture"]
)

response = risk_identification_chain(request)
print("Identified Risks:")
for i, risk in enumerate(response.risks, 1):
    print(f"{i}. {risk.title}: {risk.description}")
```