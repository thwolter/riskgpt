# Get Assessment

The `get_assessment` chain evaluates the potential impact of a risk. It either returns a three-point estimate with a probability distribution or, for single-event risks, an impact and probability.

## Input

`AssessmentRequest`
- `business_context` (`BusinessContext`): project information and language.
- `risk_description` (`str`): description of the risk.
- `document_refs` (`List[str]`, optional): document IDs from the microservice.

## Output

`AssessmentResponse`
- `minimum` (`float | None`): lower bound of the impact estimate.
- `most_likely` (`float | None`): most likely impact value.
- `maximum` (`float | None`): upper bound of the impact estimate.
- `distribution` (`str | None`): suggested probability distribution.
- `impact` (`float | None`): impact value for single events.
- `probability` (`float | None`): probability of occurrence for single events.
- `evidence` (`str | None`): explanation of the assessment and supporting rationale.
- `references` (`List[str] | None`): supporting references.
- `response_info` (`ResponseInfo | None`): meta-information including token usage.

## Example

```python
from src.chains.risk_assessment import risk_assessment_chain
from src.models.schemas import AssessmentRequest, BusinessContext

request = AssessmentRequest(
    business_context=BusinessContext(
        project_id="123",
        language="de",
    ),
    risk_description="Systemausfall durch mangelnde Wartung kann zu Produktionsstopps führen.",
)

response = risk_assessment_chain(request)
print(response.evidence)
```
