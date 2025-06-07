import pytest

pytest.importorskip("langgraph")

from riskgpt.models.schemas import ExternalContextRequest
from riskgpt.workflows import external_context_enrichment


def test_external_context_enrichment_basic():
    req = ExternalContextRequest(
        project_name="Test Project",
        business_context="infrastructure",
        focus_keywords=["supply"],
    )
    resp = external_context_enrichment(req)
    assert resp.sector_summary
    assert isinstance(resp.external_risks, list)
    assert isinstance(resp.source_table, list)


def test_external_context_enrichment_missing_param():
    with pytest.raises(TypeError):
        ExternalContextRequest()


def test_external_context_sources_have_url():
    req = ExternalContextRequest(
        project_name="Demo",
        business_context="tech",
    )
    resp = external_context_enrichment(req)
    for src in resp.source_table:
        assert src.get("url")


def test_external_context_demo_company():
    req = ExternalContextRequest(
        project_name="Energy Company",
        business_context="fiber optic infrastructure",
        focus_keywords=["cyber"],
    )
    resp = external_context_enrichment(req)
    assert resp.sector_summary

