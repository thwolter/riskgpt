from unittest.mock import patch

import pytest

from riskgpt.chains.get_opportunities import get_opportunities_chain
from riskgpt.models.schemas import (
    BusinessContext,
    LanguageEnum,
    OpportunityRequest,
    OpportunityResponse,
    ResponseInfo,
)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_opportunities_chain():
    """Test the get_opportunities_chain function with real API calls."""
    request = OpportunityRequest(
        business_context=BusinessContext(
            project_id="test_get_opportunities",
            project_description="A new IT project to implement a CRM system.",
            domain_knowledge="The company operates in the B2B sector.",
            language=LanguageEnum.english,
        ),
        risks=[
            "Data loss due to system failure",
            "Integration issues with legacy systems",
        ],
    )
    response = await get_opportunities_chain(request)
    assert isinstance(response.opportunities, list)
    assert len(response.opportunities) > 0


@pytest.mark.asyncio
async def test_get_opportunities_chain_with_mock():
    """Test get_opportunities_chain with mocked BaseChain.invoke."""
    request = OpportunityRequest(
        business_context=BusinessContext(
            project_id="mock",
            project_description="Mock project",
            language=LanguageEnum.english,
        ),
        risks=["Mock risk"],
    )
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
        resp = await get_opportunities_chain(request)
        assert resp.opportunities == expected.opportunities
