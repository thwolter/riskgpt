import os
from unittest.mock import patch

import pytest

from riskgpt.chains.get_correlation_tags import get_correlation_tags_chain
from riskgpt.models.schemas import (
    BusinessContext,
    CorrelationTagRequest,
    CorrelationTagResponse,
    ResponseInfo,
)


@pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set"
)
@pytest.mark.integration
def test_get_correlation_tags_chain():
    request = CorrelationTagRequest(
        business_context=BusinessContext(
            project_id="test_tags", project_description="CRM rollout", language="en"
        ),
        risk_titles=["Data loss", "Integration delay"],
        known_drivers=["legacy systems"],
    )
    response = get_correlation_tags_chain(request)
    assert isinstance(response.tags, list)


@pytest.mark.asyncio
async def test_get_correlation_tags_chain_with_mock():
    """Test correlation tag chain with mocked BaseChain.invoke."""
    request = CorrelationTagRequest(
        business_context=BusinessContext(
            project_id="mock", project_description="demo", language="en"
        ),
        risk_titles=["Data"],
    )
    expected = CorrelationTagResponse(
        tags=["finance"],
        response_info=ResponseInfo(
            consumed_tokens=5,
            total_cost=0.0,
            prompt_name="get_correlation_tags",
            model_name="mock-model",
        ),
    )

    async def mock_invoke(*args, **kwargs):
        return expected

    with patch("riskgpt.chains.base.BaseChain.invoke", side_effect=mock_invoke):
        resp = await get_correlation_tags_chain(request)
        assert resp.tags == expected.tags
