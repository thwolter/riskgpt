import os

import pytest
from unittest.mock import patch
from riskgpt.models.schemas import CorrelationTagResponse, ResponseInfo

from riskgpt.chains.get_correlation_tags import get_correlation_tags_chain
from riskgpt.models.schemas import BusinessContext, CorrelationTagRequest


@pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set"
)
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

from unittest.mock import patch
from riskgpt.models.schemas import CorrelationTagResponse, ResponseInfo


def test_get_correlation_tags_chain_with_mock():
    """Test correlation tag chain with mocked BaseChain.invoke."""
    request = CorrelationTagRequest(
        business_context=BusinessContext(project_id="mock", project_description="demo", language="en"),
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
    with patch("riskgpt.chains.base.BaseChain.invoke", return_value=expected):
        resp = get_correlation_tags_chain(request)
        assert resp.tags == expected.tags
