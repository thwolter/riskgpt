from unittest.mock import patch

import pytest

from riskgpt.chains.get_monitoring import get_monitoring_chain
from riskgpt.models.schemas import (
    BusinessContext,
    LanguageEnum,
    MonitoringRequest,
    MonitoringResponse,
    ResponseInfo,
)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_monitoring_chain():
    """Test the get_monitoring_chain function with real API calls."""
    request = MonitoringRequest(
        business_context=BusinessContext(
            project_id="test_get_monitoring",
            project_description="A new IT project to implement a CRM system.",
            domain_knowledge="The company operates in the B2B sector.",
            language=LanguageEnum.english,
        ),
        risk_description="Data loss due to system failure",
    )
    response = await get_monitoring_chain(request)
    assert isinstance(response.indicators, list)
    assert len(response.indicators) > 0


@pytest.mark.asyncio
async def test_get_monitoring_chain_with_mock():
    """Test get_monitoring_chain with mocked BaseChain.invoke."""
    request = MonitoringRequest(
        business_context=BusinessContext(
            project_id="mock",
            project_description="Mock project",
            language=LanguageEnum.english,
        ),
        risk_description="Mock risk",
    )
    expected = MonitoringResponse(
        indicators=["Mock indicator 1", "Mock indicator 2"],
        response_info=ResponseInfo(
            consumed_tokens=5,
            total_cost=0.0,
            prompt_name="get_monitoring",
            model_name="mock-model",
        ),
    )

    async def mock_invoke(*args, **kwargs):
        return expected

    with patch("riskgpt.chains.base.BaseChain.invoke", side_effect=mock_invoke):
        resp = await get_monitoring_chain(request)
        assert resp.indicators == expected.indicators
