import os

import pytest
from unittest.mock import patch
from riskgpt.models.schemas import AssessmentResponse, ResponseInfo

from riskgpt.chains.get_assessment import get_assessment_chain
from riskgpt.models.schemas import AssessmentRequest, BusinessContext


@pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set"
)
def test_get_assessment_chain():
    request = AssessmentRequest(
        business_context=BusinessContext(project_id="123", language="de"),
        risk_description="Ein Systemausfall kann zu Produktionsstopps f\u00fchren.",
    )
    response = get_assessment_chain(request)
    assert hasattr(response, "evidence")



def test_get_assessment_chain_with_mock():
    """Test get_assessment_chain with mocked BaseChain.invoke."""
    request = AssessmentRequest(
        business_context=BusinessContext(project_id="mock", language="en"),
        risk_description="System outage",
    )
    expected = AssessmentResponse(
        impact=0.5,
        probability=0.2,
        evidence="mocked",
        response_info=ResponseInfo(
            consumed_tokens=5,
            total_cost=0.0,
            prompt_name="get_assessment",
            model_name="mock-model",
        ),
    )
    with patch("riskgpt.chains.base.BaseChain.invoke", return_value=expected):
        resp = get_assessment_chain(request)
        assert resp.impact == expected.impact
        assert resp.evidence == expected.evidence
