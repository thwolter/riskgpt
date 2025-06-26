from unittest.mock import patch

import pytest

from src import risk_mitigations_chain
from src import RiskDriver
from src import (
    Mitigation,
    MitigationRequest,
    MitigationResponse,
)
from src import Risk
from src import BusinessContext


@pytest.fixture
def test_request():
    return MitigationRequest(
        business_context=BusinessContext(
            project_id="Investment-123",
            project_description="Investment in new production line",
            domain_knowledge="Manufacturing",
        ),
        risk=Risk(
            title="Outdated Hardware",
            description="The current hardware is outdated and may lead to production delays.",
        ),
        risk_drivers=[
            RiskDriver(
                driver="Hardware Age",
                explanation="The hardware is over 5 years old and may not perform optimally.",
                influences="likelihood",
            ),
            RiskDriver(
                driver="Hardware Quality",
                explanation="The hardware is not adequately calibrated and may not perform optimally.",
                influences="likelihood",
            ),
        ],
    )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_mitigations_chain(test_request):
    response = await risk_mitigations_chain(test_request)
    assert isinstance(response.mitigations, list)


@pytest.mark.asyncio
async def test_get_mitigations_chain_with_mock(test_request):
    expected = MitigationResponse(
        mitigations=[
            Mitigation(
                driver="Hardware Age",
                mitigation="Upgrade hardware to the latest model",
                explanation="Upgrading the hardware will ensure optimal performance and reduce the likelihood of production delays.",
            ),
        ]
    )

    async def mock_invoke(*args, **kwargs):
        return expected

    with patch("src.chains.base.BaseChain.invoke", side_effect=mock_invoke):
        resp = await risk_mitigations_chain(test_request)
        assert resp.mitigations == expected.mitigations
