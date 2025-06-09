from riskgpt.chains.bias_check import bias_check_chain
from riskgpt.models.schemas import BiasCheckRequest, BusinessContext


def test_bias_check_chain():
    request = BiasCheckRequest(
        business_context=BusinessContext(project_id="test_bias"),
        risk_description="This will always fail due to recent issues.",
    )
    response = bias_check_chain(request)
    assert isinstance(response.biases, list)
