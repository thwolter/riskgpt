import os

import pytest
from unittest.mock import patch
from riskgpt.models.schemas import MitigationResponse, ResponseInfo

from riskgpt.chains.get_mitigations import get_mitigations_chain
from riskgpt.models.schemas import BusinessContext, MitigationRequest


@pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set"
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

from unittest.mock import patch
from riskgpt.models.schemas import MitigationResponse, ResponseInfo


def test_get_mitigations_chain_with_mock():
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
    with patch("riskgpt.chains.base.BaseChain.invoke", return_value=expected):
        resp = get_mitigations_chain(request)
        assert resp.mitigations == expected.mitigations
