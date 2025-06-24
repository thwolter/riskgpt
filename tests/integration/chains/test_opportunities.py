from unittest.mock import patch

import pytest

from src.chains.opportunities import opportunities_chain
from src.models.chains.opportunity import (
    Opportunity,
    OpportunityRequest,
    OpportunityResponse,
)
from src.models.chains.risk import Risk
from src.models.common import BusinessContext


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
    response = await opportunities_chain(test_request)
    assert isinstance(response.opportunities, list)
    assert len(response.opportunities) > 0


@pytest.mark.asyncio
async def test_get_opportunities_chain_with_mock(test_request):
    expected = OpportunityResponse(
        opportunities=[
            Opportunity(
                opportunity="Leverage alternative suppliers to mitigate supply chain risks.",
                explanation="Identifying and engaging with alternative suppliers can help reduce dependency on a single source, thereby minimizing the impact of potential supply chain disruptions.",
            )
        ],
    )

    async def mock_invoke(*args, **kwargs):
        return expected

    with patch("src.chains.base.BaseChain.invoke", side_effect=mock_invoke):
        resp = await opportunities_chain(test_request)
        assert resp.opportunities == expected.opportunities
