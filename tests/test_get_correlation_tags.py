


from riskgpt.chains.get_correlation_tags import get_correlation_tags_chain
from riskgpt.models.schemas import CorrelationTagRequest


def test_get_correlation_tags_chain():
    request = CorrelationTagRequest(
        project_description="CRM rollout",
        risk_titles=["Data loss", "Integration delay"],
        known_drivers=["legacy systems"],
        language="en",
    )
    response = get_correlation_tags_chain(request)
    assert isinstance(response.tags, list)
