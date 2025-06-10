import os
from unittest.mock import patch
from riskgpt.models.schemas import BiasCheckRequest, BusinessContext, BiasCheckResponse, ResponseInfo

import pytest

from riskgpt.chains.bias_check import bias_check_chain

@pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set"
)
def test_bias_check_chain():
    request = BiasCheckRequest(
        business_context=BusinessContext(project_id="test_bias"),
        risk_description="This will always fail due to recent issues.",
    )
    response = bias_check_chain(request)
    assert isinstance(response.biases, list)

def test_bias_check_chain_with_mock():
    """Test bias_check_chain with mocked BaseChain.invoke."""
    request = BiasCheckRequest(
        business_context=BusinessContext(project_id="mock"),
        risk_description="This risk is biased.",
    )
    expected = BiasCheckResponse(
        biases=["recency"],
        suggestions="Avoid biased wording",
        response_info=ResponseInfo(
            consumed_tokens=10,
            total_cost=0.0,
            prompt_name="bias_check",
            model_name="mock-model",
        ),
    )
    with patch("riskgpt.chains.base.BaseChain.invoke", return_value=expected):
        resp = bias_check_chain(request)
        assert resp.biases == expected.biases
        assert resp.suggestions == expected.suggestions
