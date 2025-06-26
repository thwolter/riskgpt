from unittest.mock import patch

import pytest

from src.riskgpt.chains.risk_assessment import risk_assessment_chain
from src.riskgpt.models.chains.assessment import AssessmentRequest, AssessmentResponse
from src.riskgpt.models.common import BusinessContext


@pytest.fixture
def test_request():
    return AssessmentRequest(
        business_context=BusinessContext(
            project_id="CRM-2023",
            project_description="Investment in new CRM system",
            domain_knowledge="Our company is investing in a new CRM system to improve customer relations.",
        ),
        risk_title="CRM System Implementation Risk",
        risk_description="There is a risk that the CRM system implementation will not meet the expected requirements, leading to potential delays and increased costs.",
    )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_assessment_chain(test_request):
    response = await risk_assessment_chain(test_request)
    assert hasattr(response, "impact")
    assert response.impact is not None


@pytest.mark.asyncio
async def test_get_assessment_chain_with_mock(test_request):
    expected = AssessmentResponse(
        impact=0.5,
        probability=0.2,
        evidence="mocked",
    )

    async def mock_invoke(*args, **kwargs):
        return expected

    with patch("src.riskgpt.chains.base.BaseChain.invoke", side_effect=mock_invoke):
        resp = await risk_assessment_chain(test_request)
        assert resp.impact == expected.impact
        assert resp.evidence == expected.evidence
