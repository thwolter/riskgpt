import os

import pytest

from src import (
    AudienceEnum,
    BusinessContext,
    LanguageEnum,
    PresentationRequest,
    PresentationResponse,
    ResponseInfo,
    prepare_presentation_output,
)

audiences = [
    AudienceEnum.executive,
    # Add other audiences as needed
]


@pytest.fixture
def test_request():
    return PresentationRequest(
        business_context=BusinessContext(
            project_id="CRM-2023",
            project_description="Development of a new CRM system",
            domain_knowledge="Customer relationship management",
        ),
        audience=AudienceEnum.executive,
        focus_areas=["Technical"],
        language=LanguageEnum.english,
    )


@pytest.mark.parametrize("audience", audiences)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_prepare_presentation_all_audiences(monkeypatch, test_request):
    # If OPENAI_API_KEY is not set, mock the prepare_presentation_output function
    if not os.environ.get("OPENAI_API_KEY"):

        async def mock_prepare_presentation_output(request):
            return PresentationResponse(
                executive_summary="Mock executive summary",
                main_risks=["Mock risk 1", "Mock risk 2"],
                response_info=ResponseInfo(
                    consumed_tokens=100,
                    total_cost=0.01,
                    prompt_name="mock_prepare_presentation_output",
                    model_name="mock-model",
                ),
            )

        monkeypatch.setattr(
            "src.workflows.prepare_presentation_output.prepare_presentation_output",
            mock_prepare_presentation_output,
        )

    resp = await prepare_presentation_output(test_request)
    assert resp.executive_summary
    assert resp.main_risks
    assert resp.response_info is not None
