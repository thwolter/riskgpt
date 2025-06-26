from unittest.mock import patch

import pytest

from src.riskgpt.chains.correlation_tags import correlation_tags_chain
from src.riskgpt.models.chains.correlation import (
    CorrelationTag,
    CorrelationTagRequest,
    CorrelationTagResponse,
)
from src.riskgpt.models.chains.risk import Risk
from src.riskgpt.models.common import BusinessContext


@pytest.fixture
def test_request():
    """Fixture for a sample CorrelationTagRequest."""
    return CorrelationTagRequest(
        business_context=BusinessContext(
            project_id="New Policy Project",
            project_description="A project to develop and implement a new insurance policy",
            domain_knowledge="The company operates in the energy sector.",
        ),
        risks=[
            Risk(
                title="Data Breach",
                description="Unauthorized access to sensitive data",
                id="risk-1",
            ),
            Risk(
                title="Regulatory Compliance",
                description="Failure to comply with regulations",
                id="risk-2",
            ),
            Risk(
                title="Market Volatility",
                description="Fluctuations in market prices affecting investments",
                id="risk-3",
            ),
        ],
        known_drivers=["economic downturn", "technological change"],
    )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_correlation_tags_chain(test_request):
    response = await correlation_tags_chain(test_request)
    assert isinstance(response.correlation_tags, list)


@pytest.mark.asyncio
async def test_get_correlation_tags_chain_with_mock(test_request):
    """Test correlation tag chain with mocked BaseChain.invoke."""

    expected = CorrelationTagResponse(
        correlation_tags=[
            CorrelationTag(
                tag="Data Security",
                justification="Risks related to data security are often interconnected, especially in the context of regulatory compliance and data breaches.",
                risk_ids=["risk-1", "risk-2"],
            ),
        ]
    )

    async def mock_invoke(*args, **kwargs):
        return expected

    with patch("src.riskgpt.chains.base.BaseChain.invoke", side_effect=mock_invoke):
        resp = await correlation_tags_chain(test_request)
        assert resp.correlation_tags == expected.correlation_tags
