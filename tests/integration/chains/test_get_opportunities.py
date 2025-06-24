from unittest.mock import patch

import pytest

from riskgpt.chains import get_opportunities_chain
from riskgpt.models import (
    BusinessContext,
    ResponseInfo,
)
from riskgpt.models.chains.opportunity import OpportunityRequest, OpportunityResponse
from riskgpt.models.chains.risk import Risk


@pytest.fixture
def test_request():
    """Fixture to create a sample OpportunityRequest."""
    return OpportunityRequest(
        business_context=BusinessContext(
            project_id="ProcurementProject",
            project_description="A project focused on optimizing procurement processes.",
            domain_knowledge="Procurement, supply chain management, and cost optimization.",
        ),
        risk=Risk(
            title="Supply Chain Disruption",
            description="Risk of delays in supply chain affecting project timelines.",
            category="Operational Risk",
        ),
    )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_opportunities_chain(test_request):
    response = await get_opportunities_chain(test_request)
    assert isinstance(response.opportunities, list)
    assert len(response.opportunities) > 0


@pytest.mark.asyncio
async def test_get_opportunities_chain_with_mock(test_request):
    expected = OpportunityResponse(
        opportunities=["Mock opportunity 1", "Mock opportunity 2"],
        response_info=ResponseInfo(
            consumed_tokens=5,
            total_cost=0.0,
            prompt_name="get_opportunities",
            model_name="mock-model",
        ),
    )

    async def mock_invoke(*args, **kwargs):
        return expected

    with patch("riskgpt.chains.base.BaseChain.invoke", side_effect=mock_invoke):
        resp = await get_opportunities_chain(test_request)
        assert resp.opportunities == expected.opportunities
