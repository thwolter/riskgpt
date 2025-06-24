from unittest.mock import patch

import pytest
from models.chains.risk import IdentifiedRisk

from riskgpt.chains.get_risks import get_risks_chain
from riskgpt.models import (
    BusinessContext,
    Risk,
    RiskRequest,
    RiskResponse,
)


@pytest.fixture
def test_request():
    return RiskRequest(
        business_context=BusinessContext(
            project_id="CRM-2023",
            project_description="Development of a new CRM system",
            domain_knowledge="Customer relationship management",
        ),
        category="Technical",
        existing_risks=[
            Risk(
                title="Data migration failure",
                description="Risk of losing critical customer data during migration to the new CRM system",
                category="Technical",
            )
        ],
    )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_risks_chain(test_request):
    response = await get_risks_chain(test_request)
    assert isinstance(response.risks, list)


@pytest.mark.asyncio
async def test_get_risks_chain_with_mock(test_request):
    expected = RiskResponse(
        risks=[IdentifiedRisk(title="mock", description="desc")],
    )

    async def mock_invoke(*args, **kwargs):
        return expected

    with patch("riskgpt.chains.base.BaseChain.invoke", side_effect=mock_invoke):
        resp = await get_risks_chain(test_request)
        assert resp.risks == expected.risks
