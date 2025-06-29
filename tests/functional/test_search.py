import os
from unittest.mock import patch

import pytest
from riskgpt.helpers.search import _google_search, _wikipedia_search, search
from riskgpt.models.utils.search import SearchRequest, SearchResponse, SearchResult


@pytest.mark.skipif(
    not os.environ.get("GOOGLE_API_KEY") or not os.environ.get("GOOGLE_CSE_ID"),
    reason="Google API key or CSE ID not set",
)
@pytest.mark.integration
def test_google_search():
    """Test Google Custom Search API."""
    request = SearchRequest(query="artificial intelligence", source_type="test")
    response = _google_search(request)

    assert response.success is True
    assert len(response.results) > 0
    for result in response.results:
        assert result.title
        assert result.url
        assert result.type
        assert result.type == "test"


@pytest.mark.integration
def test_wikipedia_search():
    """Test Wikipedia search."""
    request = SearchRequest(query="artificial intelligence", source_type="test")
    response = _wikipedia_search(request)

    assert response.success is True
    assert len(response.results) > 0
    for result in response.results:
        assert result.title
        assert result.url
        assert result.type
        assert result.type == "test"
        assert "Wikipedia:" in result.title


@pytest.mark.skipif(
    not os.environ.get("GOOGLE_API_KEY") or not os.environ.get("GOOGLE_CSE_ID"),
    reason="Google API key, CSE ID, or Wikipedia integration not set",
)
@pytest.mark.integration
def test_combined_search(monkeypatch):
    """Test combined search with Google and Wikipedia."""

    # Use monkeypatch instead of directly modifying os.environ
    monkeypatch.setattr("riskgpt.helpers.search.settings.SEARCH_PROVIDER", "google")
    monkeypatch.setattr("riskgpt.helpers.search.settings.INCLUDE_WIKIPEDIA", True)

    request = SearchRequest(query="artificial intelligence", source_type="test")
    response = search(request)

    assert response.success is True
    assert len(response.results) > 0

    # Check if we have both Google and Wikipedia results
    has_wikipedia = False
    has_google = False

    for result in response.results:
        if "Wikipedia:" in result.title:
            has_wikipedia = True
        else:
            has_google = True

    assert has_wikipedia, "No Wikipedia results found"
    assert has_google, "No Google results found"


@pytest.fixture
def mock_settings(monkeypatch):
    """Fixture to patch the settings to use tavily as the search provider."""
    monkeypatch.setattr("riskgpt.helpers.search.settings.SEARCH_PROVIDER", "tavily")
    monkeypatch.setattr("riskgpt.helpers.search.settings.INCLUDE_WIKIPEDIA", False)
    monkeypatch.setattr("riskgpt.helpers.search.settings.MAX_SEARCH_RESULTS", 2)
    yield


@pytest.fixture
def search_request():
    """Fixture to create a SearchRequest object."""
    return SearchRequest(query="test query", source_type="news")


# Fixtures for mocking search functions
@pytest.fixture
def mock_google_search():
    """Fixture to mock Google search function."""
    return SearchResponse(
        results=[
            SearchResult(
                title="G",
                url="u",
                date="",
                type="news",
                content="c",
            )
        ],
        success=True,
        error_message="",
    )


@pytest.fixture
def mock_wikipedia_search():
    """Fixture to mock Wikipedia search function."""
    return SearchResponse(
        results=[
            SearchResult(
                title="W",
                url="u",
                date="",
                type="news",
                content="c",
            )
        ],
        success=True,
        error_message="",
    )


@pytest.fixture
def mock_duckduckgo_search():
    """Fixture to mock DuckDuckGo search function."""
    return SearchResponse(
        results=[
            SearchResult(
                title="D",
                url="u",
                date="",
                type="news",
                content="c",
            )
        ],
        success=True,
        error_message="",
    )


def test_search_google_with_mock(
    monkeypatch, search_request, mock_google_search, mock_wikipedia_search
):
    """Search using mocked Google provider."""
    monkeypatch.setattr("riskgpt.helpers.search.settings.SEARCH_PROVIDER", "google")
    monkeypatch.setattr("riskgpt.helpers.search.settings.INCLUDE_WIKIPEDIA", True)

    with (
        patch(
            "riskgpt.helpers.search._google_search",
            return_value=mock_google_search,
        ),
        patch(
            "riskgpt.helpers.search._wikipedia_search",
            return_value=mock_wikipedia_search,
        ),
    ):
        search_response: SearchResponse = search(search_request)
        assert search_response.success is True
        assert any(result.title == "G" for result in search_response.results)
        assert any(result.title == "W" for result in search_response.results)

    monkeypatch.setattr("riskgpt.helpers.search.settings.INCLUDE_WIKIPEDIA", False)
    with patch(
        "riskgpt.helpers.search._google_search",
        return_value=mock_google_search,
    ):
        search_response: SearchResponse = search(search_request)
        assert search_response.success is True
        assert search_response.results[0].title == "G"


def test_search_duckduckgo_with_mock(
    monkeypatch, search_request, mock_duckduckgo_search, mock_wikipedia_search
):
    """Search using mocked DuckDuckGo provider."""
    monkeypatch.setattr("riskgpt.helpers.search.settings.SEARCH_PROVIDER", "duckduckgo")
    monkeypatch.setattr("riskgpt.helpers.search.settings.INCLUDE_WIKIPEDIA", True)

    with (
        patch(
            "riskgpt.helpers.search._duckduckgo_search",
            return_value=mock_duckduckgo_search,
        ),
        patch(
            "riskgpt.helpers.search._wikipedia_search",
            return_value=mock_wikipedia_search,
        ),
    ):
        search_response: SearchResponse = search(search_request)
        assert search_response.success is True
        assert any(result.title == "D" for result in search_response.results)
        assert any(result.title == "W" for result in search_response.results)

    # Test with INCLUDE_WIKIPEDIA disabled
    monkeypatch.setattr("riskgpt.helpers.search.settings.INCLUDE_WIKIPEDIA", False)
    with patch(
        "riskgpt.helpers.search._duckduckgo_search",
        return_value=mock_duckduckgo_search,
    ):
        search_response: SearchResponse = search(search_request)
        assert search_response.success is True
        assert search_response.results[0].title == "D"


def test_search_wikipedia_with_mock(monkeypatch, search_request, mock_wikipedia_search):
    """Search using mocked Wikipedia provider."""
    monkeypatch.setattr("riskgpt.helpers.search.settings.SEARCH_PROVIDER", "wikipedia")
    with patch(
        "riskgpt.helpers.search._wikipedia_search",
        return_value=mock_wikipedia_search,
    ):
        search_response: SearchResponse = search(search_request)
        assert search_response.success is True
        assert search_response.results[0].title.startswith("W")
