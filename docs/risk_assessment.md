# Risk Assessment

The `risk_assessment_chain` evaluates the potential impact of a risk. It either returns a three-point estimate with a probability distribution or, for single-event risks, an impact and probability.

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
from riskgpt import risk_assessment_chain
from riskgpt.models.common import BusinessContext
from riskgpt.models.chains import AssessmentRequest

request = AssessmentRequest(
    business_context=BusinessContext(
        project_id="ACME-MFG-2023",
        project_name="ACME Manufacturing Plant Upgrade",
        project_description="Modernization of production line equipment and control systems",
        language="de",
    ),
    risk_description="Systemausfall durch mangelnde Wartung kann zu Produktionsstopps führen und erhebliche finanzielle Verluste verursachen.",
    document_refs=["doc-maintenance-history-2022", "doc-production-impact-analysis"]
)

response = risk_assessment_chain(request)
print(f"Impact range: {response.minimum} - {response.most_likely} - {response.maximum}")
print(f"Distribution: {response.distribution}")
print(f"Evidence: {response.evidence}")
```