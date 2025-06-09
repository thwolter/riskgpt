import pytest

from riskgpt.models.schemas import (
    AudienceEnum,
    BusinessContext,
    LanguageEnum,
    PresentationRequest,
)
from riskgpt.workflows import prepare_presentation_output

audiences = [
    AudienceEnum.executive,
    # Add other audiences as needed
]


@pytest.mark.parametrize("audience", audiences)
def test_prepare_presentation_all_audiences(audience):
    request = PresentationRequest(
        business_context=BusinessContext(
            project_id="p1",
            project_description="CRM rollout",
            language=LanguageEnum.english,
        ),
        audience=audience,
        focus_areas=["Technical"],
    )
    resp = prepare_presentation_output(request)
    assert resp.executive_summary
    assert resp.main_risks
    assert resp.response_info is not None
