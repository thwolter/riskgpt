# Get Assessment

The `get_assessment` chain evaluates the potential impact of a risk. It either returns a three-point estimate with a probability distribution or, for single-event risks, an impact and probability.

## Input

`AssessmentRequest`
- `project_id` (`str`): unique identifier of the project.
- `risk_description` (`str`): description of the risk.
- `domain_knowledge` (`str`, optional): additional domain-specific context.
- `language` (`str`, optional, default `"en"`): language for the response.

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
from riskgpt.chains.get_assessment import get_assessment_chain
from riskgpt.models.schemas import AssessmentRequest

request = AssessmentRequest(
    project_id="123",
    risk_description="Systemausfall durch mangelnde Wartung kann zu Produktionsstopps führen.",
    language="de"
)

response = get_assessment_chain(request)
print(response.evidence)
```
