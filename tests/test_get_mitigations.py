import os

import pytest

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
