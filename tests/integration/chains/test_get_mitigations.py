from unittest.mock import patch

import pytest

from riskgpt.chains.get_mitigations import get_mitigations_chain
from riskgpt.models.schemas import (
    BusinessContext,
    MitigationRequest,
    MitigationResponse,
    ResponseInfo,
)


@pytest.mark.integration
def test_get_mitigations_chain():
    request = MitigationRequest(
        business_context=BusinessContext(
            project_id="123",
            domain_knowledge="Das Unternehmen ist im B2B-Bereich tätig.",
            language="de",
        ),
        risk_description="Ein Systemausfall kann zu Produktionsstopps führen.",
        drivers=["veraltete Hardware"],
    )
    response = get_mitigations_chain(request)
    assert isinstance(response.mitigations, list)


@pytest.mark.asyncio
async def test_get_mitigations_chain_with_mock():
    """Test get_mitigations_chain with mocked BaseChain.invoke."""
    request = MitigationRequest(
        business_context=BusinessContext(project_id="mock", language="en"),
        risk_description="Failure",
        drivers=["legacy"],
    )
    expected = MitigationResponse(
        mitigations=["Upgrade"],
        response_info=ResponseInfo(
            consumed_tokens=5,
            total_cost=0.0,
            prompt_name="get_mitigations",
            model_name="mock-model",
        ),
    )

    async def mock_invoke(*args, **kwargs):
        return expected

    with patch("riskgpt.chains.base.BaseChain.invoke", side_effect=mock_invoke):
        resp = await get_mitigations_chain(request)
        assert resp.mitigations == expected.mitigations
