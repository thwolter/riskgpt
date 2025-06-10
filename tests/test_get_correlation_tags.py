import os

import pytest

from riskgpt.chains.get_correlation_tags import get_correlation_tags_chain
from riskgpt.models.schemas import BusinessContext, CorrelationTagRequest


@pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set"
)
@pytest.mark.integration
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
