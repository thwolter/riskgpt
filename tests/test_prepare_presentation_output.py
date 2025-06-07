import pytest

pytest.importorskip("langgraph")

from riskgpt.workflows import prepare_presentation_output
from riskgpt.models.schemas import PresentationRequest


def test_prepare_presentation_executive():
    request = PresentationRequest(
        project_id="p1",
        project_description="CRM rollout",
        audience="executive",
        focus_areas=["Technical"],
        language="en",
    )
    resp = prepare_presentation_output(request)
    assert resp.executive_summary
    assert isinstance(resp.main_risks, list)
    assert resp.key_drivers is not None
    assert resp.mitigations is not None
    assert resp.response_info is not None


def test_prepare_presentation_workshop():
    request = PresentationRequest(
        project_id="p2",
        project_description="ERP migration",
        audience="workshop",
        focus_areas=["Technical"],
        language="en",
    )
    resp = prepare_presentation_output(request)
    assert resp.mitigations is not None
    assert resp.key_drivers is not None
    assert resp.response_info is not None

