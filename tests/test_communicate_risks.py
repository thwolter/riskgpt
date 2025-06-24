from unittest.mock import patch

import pytest

from riskgpt.chains.communicate_risks import communicate_risks_chain
from riskgpt.models.schemas import (
    BusinessContext,
    CommunicationRequest,
    CommunicationResponse,
    LanguageEnum,
    ResponseInfo,
)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_communicate_risks_chain():
    """Test the communicate_risks_chain function with real API calls."""
    request = CommunicationRequest(
        business_context=BusinessContext(
            project_id="test_communicate_risks",
            project_description="A new IT project to implement a CRM system.",
            domain_knowledge="The company operates in the B2B sector.",
            language=LanguageEnum.english,
        ),
        summary="The project aims to implement a CRM system to improve customer relationship management.",
    )
    response = await communicate_risks_chain(request)
    assert response.summary is not None
    assert response.key_points is not None


@pytest.mark.asyncio
async def test_communicate_risks_chain_with_mock():
    """Test communicate_risks_chain with mocked BaseChain.invoke."""
    request = CommunicationRequest(
        business_context=BusinessContext(
            project_id="mock",
            project_description="Mock project",
            language=LanguageEnum.english,
        ),
        risks=["Mock risk"],
        audience="technical",
    )
    expected = CommunicationResponse(
        summary="Mock summary",
        key_points=["Mock key point"],
        response_info=ResponseInfo(
            consumed_tokens=5,
            total_cost=0.0,
            prompt_name="communicate_risks",
            model_name="mock-model",
        ),
    )

    async def mock_invoke(*args, **kwargs):
        return expected

    with patch("riskgpt.chains.base.BaseChain.invoke", side_effect=mock_invoke):
        resp = await communicate_risks_chain(request)
        assert resp.summary == expected.summary
        assert resp.key_points == expected.key_points
