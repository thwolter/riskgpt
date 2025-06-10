import os

import pydantic
import pytest
from unittest.mock import patch

from riskgpt.models.schemas import BusinessContext, ExternalContextRequest
from riskgpt.workflows import external_context_enrichment


def test_external_context_enrichment_basic():
    req = ExternalContextRequest(
        business_context=BusinessContext(
            project_id="test_basic",
            project_description="Test Project",
            domain_knowledge="infrastructure",
        ),
        focus_keywords=["supply"],
    )
    resp = external_context_enrichment(req)
    assert resp.sector_summary
    assert isinstance(resp.external_risks, list)
    assert isinstance(resp.source_table, list)


def test_external_context_enrichment_missing_param():
    with pytest.raises(pydantic.ValidationError):
        ExternalContextRequest()


def test_external_context_sources_have_url():
    req = ExternalContextRequest(
        business_context=BusinessContext(
            project_id="test_sources",
            project_description="Demo",
            domain_knowledge="tech",
        ),
    )
    resp = external_context_enrichment(req)
    for src in resp.source_table:
        assert src.get("url")


def test_external_context_demo_company():
    req = ExternalContextRequest(
        business_context=BusinessContext(
            project_id="test_demo",
            project_description="Energy Company",
            domain_knowledge="fiber optic infrastructure",
        ),
        focus_keywords=["cyber"],
    )
    resp = external_context_enrichment(req)
    assert resp.sector_summary


@pytest.mark.skipif(
    not os.environ.get("GOOGLE_API_KEY")
    or not os.environ.get("GOOGLE_CSE_ID")
    or not os.environ.get("INCLUDE_WIKIPEDIA")
    or os.environ.get("INCLUDE_WIKIPEDIA", "").lower() != "true",
    reason="Google API key, CSE ID, or Wikipedia integration not set",
)
def test_external_context_with_google_and_wikipedia():
    """Test the workflow with Google Custom Search API and Wikipedia."""

    # Save original environment variables
    original_provider = os.environ.get("SEARCH_PROVIDER")
    original_include_wiki = os.environ.get("INCLUDE_WIKIPEDIA")

    try:
        # Set environment variables for this test
        os.environ["SEARCH_PROVIDER"] = "google"
        os.environ["INCLUDE_WIKIPEDIA"] = "true"

        req = ExternalContextRequest(
            business_context=BusinessContext(
                project_id="test_ai",
                project_description="Artificial Intelligence",
                domain_knowledge="machine learning",
            ),
            focus_keywords=["ethics", "regulation"],
        )
        resp = external_context_enrichment(req)

        # Verify the response
        assert resp.sector_summary
        assert isinstance(resp.external_risks, list)
        assert isinstance(resp.source_table, list)

        # Check if we have both Google and Wikipedia results
        has_wikipedia = False
        for src in resp.source_table:
            if "Wikipedia:" in src.get("title", ""):
                has_wikipedia = True
                break

        assert has_wikipedia, "No Wikipedia results found in the response"

    finally:
        # Restore original environment variables
        if original_provider:
            os.environ["SEARCH_PROVIDER"] = original_provider
        elif "SEARCH_PROVIDER" in os.environ:
            del os.environ["SEARCH_PROVIDER"]

        if original_include_wiki:
            os.environ["INCLUDE_WIKIPEDIA"] = original_include_wiki
        elif "INCLUDE_WIKIPEDIA" in os.environ:
            del os.environ["INCLUDE_WIKIPEDIA"]

from unittest.mock import patch


def test_external_context_enrichment_with_mock():
    req = ExternalContextRequest(
        business_context=BusinessContext(project_id="mock", project_description="demo", domain_knowledge="it"),
        focus_keywords=["keyword"],
    )
    mocked_result = ([{"title": "T", "url": "u", "date": "", "type": "news", "comment": "c"}], True)
    with patch("riskgpt.workflows.external_context_enrichment.search_context", return_value=mocked_result):
        resp = external_context_enrichment(req)
        assert resp.source_table[0]["title"] == "T"
