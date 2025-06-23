from unittest.mock import patch

import pytest

from riskgpt.chains.get_drivers import get_drivers_chain
from riskgpt.models.schemas import (
    BusinessContext,
    DriverRequest,
    DriverResponse,
    LanguageEnum,
    ResponseInfo,
)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_drivers_chain():
    """Test the get_drivers_chain function with real API calls."""
    request = DriverRequest(
        business_context=BusinessContext(
            project_id="test_get_drivers",
            project_description="A new IT project to implement a CRM system.",
            domain_knowledge="The company operates in the B2B sector.",
            language=LanguageEnum.english,
        ),
        risk_description="Data loss due to system failure",
    )
    response = await get_drivers_chain(request)
    assert isinstance(response.drivers, list)
    assert len(response.drivers) > 0


@pytest.mark.asyncio
async def test_get_drivers_chain_with_mock():
    """Test get_drivers_chain with mocked BaseChain.invoke."""
    request = DriverRequest(
        business_context=BusinessContext(
            project_id="mock",
            project_description="Mock project",
            language=LanguageEnum.english,
        ),
        risk_description="Mock risk",
    )
    expected = DriverResponse(
        drivers=["Mock driver 1", "Mock driver 2"],
        response_info=ResponseInfo(
            consumed_tokens=5,
            total_cost=0.0,
            prompt_name="get_drivers",
            model_name="mock-model",
        ),
    )

    async def mock_invoke(*args, **kwargs):
        return expected

    with patch("riskgpt.chains.base.BaseChain.invoke", side_effect=mock_invoke):
        resp = await get_drivers_chain(request)
        assert resp.drivers == expected.drivers
