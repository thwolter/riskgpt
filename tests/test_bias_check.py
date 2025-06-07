from riskgpt.chains.bias_check import bias_check_chain
from riskgpt.models.schemas import BiasCheckRequest


def test_bias_check_chain():
    request = BiasCheckRequest(
        risk_description="This will always fail due to recent issues."
    )
    response = bias_check_chain(request)
    assert isinstance(response.biases, list)
