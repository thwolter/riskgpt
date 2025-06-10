import os

import pytest

from riskgpt.config.settings import RiskGPTSettings
from riskgpt.utils.search import (
    _google_search,
    _wikipedia_search,
    search,
)


@pytest.mark.skipif(
    not os.environ.get("GOOGLE_API_KEY") or not os.environ.get("GOOGLE_CSE_ID"),
    reason="Google API key or CSE ID not set",
)
@pytest.mark.integration
def test_google_search():
    """Test Google Custom Search API."""
    query = "artificial intelligence"
    source_type = "test"
    results, success = _google_search(query, source_type)

    assert success is True
    assert len(results) > 0
    for result in results:
        assert "title" in result
        assert "url" in result
        assert "type" in result
        assert result["type"] == source_type


@pytest.mark.skipif(
    not os.environ.get("INCLUDE_WIKIPEDIA")
    or os.environ.get("INCLUDE_WIKIPEDIA", "").lower() != "true",
    reason="Wikipedia integration not enabled",
)
@pytest.mark.integration
def test_wikipedia_search():
    """Test Wikipedia search."""

    query = "artificial intelligence"
    source_type = "test"
    results, success = _wikipedia_search(query, source_type)

    assert success is True
    assert len(results) > 0
    for result in results:
        assert "title" in result
        assert "url" in result
        assert "type" in result
        assert result["type"] == source_type
        assert "Wikipedia:" in result["title"]


@pytest.mark.skipif(
    not os.environ.get("GOOGLE_API_KEY")
    or not os.environ.get("GOOGLE_CSE_ID")
    or not os.environ.get("INCLUDE_WIKIPEDIA")
    or os.environ.get("INCLUDE_WIKIPEDIA", "").lower() != "true",
    reason="Google API key, CSE ID, or Wikipedia integration not set",
)
@pytest.mark.integration
def test_combined_search():
    """Test combined search with Google and Wikipedia."""

    # Temporarily set the environment variables for this test
    os.environ["SEARCH_PROVIDER"] = "google"
    os.environ["INCLUDE_WIKIPEDIA"] = "true"

    query = "artificial intelligence"
    source_type = "test"
    results, success = search(query, source_type)

    assert success is True
    assert len(results) > 0

    # Check if we have both Google and Wikipedia results
    has_wikipedia = False
    has_google = False

    for result in results:
        if "Wikipedia:" in result.get("title", ""):
            has_wikipedia = True
        else:
            has_google = True

    assert has_wikipedia, "No Wikipedia results found"
    assert has_google, "No Google results found"


def test_search_provider_selection():
    """Test that the search provider is selected correctly based on environment variables."""
    # Save original environment variables
    original_provider = os.environ.get("SEARCH_PROVIDER")

    try:
        # Test with Google
        os.environ["SEARCH_PROVIDER"] = "google"
        settings = RiskGPTSettings()
        assert settings.SEARCH_PROVIDER == "google"

        # Test with DuckDuckGo
        os.environ["SEARCH_PROVIDER"] = "duckduckgo"
        settings = RiskGPTSettings()
        assert settings.SEARCH_PROVIDER == "duckduckgo"

        # Test with Wikipedia
        os.environ["SEARCH_PROVIDER"] = "wikipedia"
        settings = RiskGPTSettings()
        assert settings.SEARCH_PROVIDER == "wikipedia"
    finally:
        # Restore original environment variable
        if original_provider:
            os.environ["SEARCH_PROVIDER"] = original_provider
        elif "SEARCH_PROVIDER" in os.environ:
            del os.environ["SEARCH_PROVIDER"]
