import os

import pytest

from riskgpt.chains.get_assessment import get_assessment_chain
from riskgpt.models.schemas import AssessmentRequest, BusinessContext


@pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set"
)
@pytest.mark.integration
def test_get_assessment_chain():
    request = AssessmentRequest(
        business_context=BusinessContext(project_id="123", language="de"),
        risk_description="Ein Systemausfall kann zu Produktionsstopps f\u00fchren.",
    )
    response = get_assessment_chain(request)
    assert hasattr(response, "evidence")
