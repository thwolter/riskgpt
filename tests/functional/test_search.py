import os
from unittest.mock import patch

import pytest

from src.config.settings import RiskGPTSettings
from src.utils.search import _google_search, _wikipedia_search, search


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
    not os.environ.get("GOOGLE_API_KEY") or not os.environ.get("GOOGLE_CSE_ID"),
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


def test_search_google_with_mock(monkeypatch):
    """Search using mocked Google provider."""
    os.environ["SEARCH_PROVIDER"] = "google"
    # Save original INCLUDE_WIKIPEDIA value
    original_include_wiki = os.environ.get("INCLUDE_WIKIPEDIA")

    try:
        # Test with INCLUDE_WIKIPEDIA enabled
        os.environ["INCLUDE_WIKIPEDIA"] = "true"
        with (
            patch(
                "src.utils.search._google_search",
                return_value=(
                    [
                        {
                            "title": "G",
                            "url": "u",
                            "date": "",
                            "type": "news",
                            "content": "c",
                        }
                    ],
                    True,
                ),
            ),
            patch(
                "src.utils.search._wikipedia_search",
                return_value=(
                    [
                        {
                            "title": "W",
                            "url": "u",
                            "date": "",
                            "type": "news",
                            "content": "c",
                        }
                    ],
                    True,
                ),
            ),
        ):
            results, success = search("q", "news")
            assert success is True
            assert any(result["title"] == "G" for result in results)
            assert any(result["title"] == "W" for result in results)

        # Test with INCLUDE_WIKIPEDIA disabled
        os.environ["INCLUDE_WIKIPEDIA"] = "false"
        with patch(
            "src.utils.search._google_search",
            return_value=(
                [
                    {
                        "title": "G",
                        "url": "u",
                        "date": "",
                        "type": "news",
                        "content": "c",
                    }
                ],
                True,
            ),
        ):
            results, success = search("q", "news")
            assert success is True
            assert results[0]["title"] == "G"
    finally:
        # Restore original INCLUDE_WIKIPEDIA value
        if original_include_wiki:
            os.environ["INCLUDE_WIKIPEDIA"] = original_include_wiki
        elif "INCLUDE_WIKIPEDIA" in os.environ:
            del os.environ["INCLUDE_WIKIPEDIA"]


def test_search_duckduckgo_with_mock(monkeypatch):
    """Search using mocked DuckDuckGo provider."""
    os.environ["SEARCH_PROVIDER"] = "duckduckgo"
    # Save original INCLUDE_WIKIPEDIA value
    original_include_wiki = os.environ.get("INCLUDE_WIKIPEDIA")

    try:
        # Test with INCLUDE_WIKIPEDIA enabled
        os.environ["INCLUDE_WIKIPEDIA"] = "true"
        with (
            patch(
                "src.utils.search._duckduckgo_search",
                return_value=(
                    [
                        {
                            "title": "D",
                            "url": "u",
                            "date": "",
                            "type": "news",
                            "content": "c",
                        }
                    ],
                    True,
                ),
            ),
            patch(
                "src.utils.search._wikipedia_search",
                return_value=(
                    [
                        {
                            "title": "W",
                            "url": "u",
                            "date": "",
                            "type": "news",
                            "content": "c",
                        }
                    ],
                    True,
                ),
            ),
        ):
            results, success = search("q", "news")
            assert success is True
            assert any(result["title"] == "D" for result in results)
            assert any(result["title"] == "W" for result in results)

        # Test with INCLUDE_WIKIPEDIA disabled
        os.environ["INCLUDE_WIKIPEDIA"] = "false"
        with patch(
            "src.utils.search._duckduckgo_search",
            return_value=(
                [
                    {
                        "title": "D",
                        "url": "u",
                        "date": "",
                        "type": "news",
                        "content": "c",
                    }
                ],
                True,
            ),
        ):
            results, success = search("q", "news")
            assert success is True
            assert results[0]["title"] == "D"
    finally:
        # Restore original INCLUDE_WIKIPEDIA value
        if original_include_wiki:
            os.environ["INCLUDE_WIKIPEDIA"] = original_include_wiki
        elif "INCLUDE_WIKIPEDIA" in os.environ:
            del os.environ["INCLUDE_WIKIPEDIA"]


def test_search_wikipedia_with_mock(monkeypatch):
    os.environ["SEARCH_PROVIDER"] = "wikipedia"
    with patch(
        "src.utils.search._wikipedia_search",
        return_value=(
            [{"title": "W", "url": "u", "date": "", "type": "news", "content": "c"}],
            True,
        ),
    ):
        results, success = search("q", "news")
        assert success is True
        assert results[0]["title"].startswith("W")
