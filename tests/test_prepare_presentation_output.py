from riskgpt.models.schemas import AudienceEnum, BusinessContext, PresentationRequest
from riskgpt.workflows import prepare_presentation_output


def test_prepare_presentation_executive():
    request = PresentationRequest(
        business_context=BusinessContext(
            project_id="p1", project_description="CRM rollout", language="en"
        ),
        audience=AudienceEnum.executive,
        focus_areas=["Technical"],
    )
    resp = prepare_presentation_output(request)
    assert resp.executive_summary
    assert isinstance(resp.main_risks, list)
    assert resp.key_drivers is not None
    assert resp.mitigations is not None
    assert resp.response_info is not None


def test_prepare_presentation_workshop():
    request = PresentationRequest(
        business_context=BusinessContext(
            project_id="p2", project_description="ERP migration", language="en"
        ),
        audience=AudienceEnum.workshop,
        focus_areas=["Technical"],
    )
    resp = prepare_presentation_output(request)
    assert resp.mitigations is not None
    assert resp.key_drivers is not None
    assert resp.response_info is not None
