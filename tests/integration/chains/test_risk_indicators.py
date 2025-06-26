from unittest.mock import patch

import pytest

from src import (
    BusinessContext,
    Risk,
    RiskIndicator,
    RiskIndicatorRequest,
    RiskIndicatorResponse,
    risk_indicators_chain,
)


@pytest.fixture
def test_request():
    """Fixture to create a sample MonitoringRequest."""
    return RiskIndicatorRequest(
        business_context=BusinessContext(
            project_id="FoundationProject",
            project_description="Founding a startup focused on AI-driven risk management solutions.",
            domain_knowledge="AI, risk management, and business strategy.",
        ),
        risk=Risk(
            title="Data Privacy Risk",
            description="Risk of data breaches affecting customer privacy.",
        ),
    )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_monitoring_chain(test_request):
    response = await risk_indicators_chain(test_request)
    assert isinstance(response.indicators, list)
    assert len(response.indicators) > 0


@pytest.mark.asyncio
async def test_get_monitoring_chain_with_mock(test_request):
    expected = RiskIndicatorResponse(
        indicators=[
            RiskIndicator(
                indicator="Data Breach Frequency",
                type="leading",
                explanation="Tracks the number of data breaches over time to identify trends.",
                action="Implement stronger data encryption and access controls.",
                reference="NIST SP 800-53 Rev. 5",
            )
        ],
    )

    async def mock_invoke(*args, **kwargs):
        return expected

    with patch("src.chains.base.BaseChain.invoke", side_effect=mock_invoke):
        resp = await risk_indicators_chain(test_request)
        assert resp.indicators == expected.indicators
