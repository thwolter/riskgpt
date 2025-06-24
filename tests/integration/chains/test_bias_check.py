import pytest

from riskgpt.chains.bias_check import bias_check_chain
from riskgpt.models.chains.bias_check import BiasCheckRequest
from riskgpt.models.common import BusinessContext


@pytest.mark.asyncio
async def test_bias_check_chain():
    request = BiasCheckRequest(
        business_context=BusinessContext(project_id="test_bias"),
        risk_description="This will always fail due to recent issues.",
    )
    response = await bias_check_chain(request)
    assert isinstance(response.biases, list)


@pytest.mark.asyncio
async def test_bias_check_chain_with_mock():
    """Test bias_check_chain with a risk description containing bias patterns."""
    request = BiasCheckRequest(
        business_context=BusinessContext(project_id="mock"),
        risk_description="This risk will always fail due to recent issues.",
    )
    resp = await bias_check_chain(request)
    assert "framing" in resp.biases
    assert "availability" in resp.biases
    assert "Avoid absolute terms like 'always' or 'never'" in resp.suggestions
    assert (
        "Check whether recent events unduly influence the assessment"
        in resp.suggestions
    )
