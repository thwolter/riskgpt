import os

import pytest

from riskgpt.chains.bias_check import bias_check_chain
from riskgpt.models.schemas import BiasCheckRequest, BusinessContext


@pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set"
)
@pytest.mark.integration
def test_bias_check_chain():
    request = BiasCheckRequest(
        business_context=BusinessContext(project_id="test_bias"),
        risk_description="This will always fail due to recent issues.",
    )
    response = bias_check_chain(request)
    assert isinstance(response.biases, list)
