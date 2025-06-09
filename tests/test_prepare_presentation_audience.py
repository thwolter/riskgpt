import pytest

from riskgpt.models.schemas import AudienceEnum, BusinessContext, PresentationRequest
from riskgpt.workflows import prepare_presentation_output

audiences = [
    AudienceEnum.executive,
    AudienceEnum.workshop,
    AudienceEnum.risk_internal,
    AudienceEnum.audit,
    AudienceEnum.regulator,
    AudienceEnum.project_owner,
    AudienceEnum.investor,
    AudienceEnum.operations,
]


@pytest.mark.parametrize("audience", audiences)
def test_prepare_presentation_all_audiences(audience):
    request = PresentationRequest(
        business_context=BusinessContext(
            project_id="p1", project_description="CRM rollout", language="en"
        ),
        audience=audience,
        focus_areas=["Technical"],
    )
    resp = prepare_presentation_output(request)
    assert resp.executive_summary
    assert resp.main_risks
    assert resp.response_info is not None
