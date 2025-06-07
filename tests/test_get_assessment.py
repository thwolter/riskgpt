from riskgpt.chains.get_assessment import get_assessment_chain
from riskgpt.models.schemas import AssessmentRequest


def test_get_assessment_chain():
    request = AssessmentRequest(
        project_id="123",
        risk_description="Ein Systemausfall kann zu Produktionsstopps f\u00fchren.",
        language="de",
    )
    response = get_assessment_chain(request)
    assert hasattr(response, "evidence")
