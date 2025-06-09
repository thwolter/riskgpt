from riskgpt.models.schemas import BusinessContext, ContextQualityRequest
from riskgpt.workflows import check_context_quality


def test_check_context_quality_incomplete():
    req = ContextQualityRequest(
        business_context=BusinessContext(
            project_id="test_incomplete", domain_knowledge="CRM update."
        ),
        project_type="IT",
    )
    resp = check_context_quality(req)
    assert isinstance(resp.shortcomings, list)
    assert isinstance(resp.suggested_improvements, str)


def test_check_context_quality_complete():
    req = ContextQualityRequest(
        business_context=BusinessContext(
            project_id="test_complete",
            domain_knowledge="Our company plans a comprehensive CRM modernization including data migration and user training.",
        ),
        project_type="IT",
    )
    resp = check_context_quality(req)
    assert isinstance(resp.rationale, str)
