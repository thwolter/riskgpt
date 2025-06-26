import pytest
from chains.check_bias import check_bias_chain
from models.chains.bias_check import BiasCheckRequest
from models.common import BusinessContext


@pytest.mark.asyncio
async def test_bias_check_chain():
    request = BiasCheckRequest(
        business_context=BusinessContext(project_id="test_bias"),
        risk_description="This will always fail due to recent issues.",
    )
    response = await check_bias_chain(request)
    assert isinstance(response.biases, list)


@pytest.mark.asyncio
async def test_bias_check_chain_with_mock():
    """Test bias_check_chain with a risk description containing bias patterns."""
    request = BiasCheckRequest(
        business_context=BusinessContext(project_id="mock"),
        risk_description="This risk will always fail due to recent issues.",
    )
    resp = await check_bias_chain(request)
    assert "framing" in resp.biases
    assert "availability" in resp.biases
    assert "Avoid absolute terms like 'always' or 'never'" in resp.suggestions
    assert (
        "Check whether recent events unduly influence the assessment"
        in resp.suggestions
    )
