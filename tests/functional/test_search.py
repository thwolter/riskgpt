import os
from typing import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from riskgpt.helpers.search import search
from riskgpt.helpers.search.google import GoogleSearchProvider
from riskgpt.helpers.search.wikipedia import WikipediaSearchProvider
from riskgpt.models.enums import TopicEnum
from riskgpt.models.helpers.search import SearchRequest, SearchResponse, SearchResult


@pytest.mark.skipif(
    not os.environ.get("GOOGLE_API_KEY") or not os.environ.get("GOOGLE_CSE_ID"),
    reason="Google API key or CSE ID not set",
)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_google_search():
    """Test Google Custom Search API."""
    request = SearchRequest(
        query="artificial intelligence", source_type=TopicEnum.LINKEDIN
    )
    google_provider = GoogleSearchProvider()
    response = await google_provider.search(request)

    assert response.success is True
    assert len(response.results) > 0
    for result in response.results:
        assert result.title
        assert result.url
        assert result.type
        assert result.type == "linkedin"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_wikipedia_search():
    """Test Wikipedia search."""
    request = SearchRequest(
        query="artificial intelligence", source_type=TopicEnum.REGULATORY, max_results=5
    )
    wiki_provider = WikipediaSearchProvider()
    response = await wiki_provider.search(request)

    assert response.success is True
    assert len(response.results) > 0
    for result in response.results:
        assert result.title
        assert result.url
        assert result.type
        assert result.type == "regulatory"


@pytest.mark.skipif(
    not os.environ.get("GOOGLE_API_KEY") or not os.environ.get("GOOGLE_CSE_ID"),
    reason="Google API key, CSE ID, or Wikipedia integration not set",
)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_combined_search(monkeypatch):
    """Test combined search with Google and Wikipedia."""

    # Use monkeypatch instead of directly modifying os.environ
    monkeypatch.setattr(
        "riskgpt.helpers.search.factory.settings.SEARCH_PROVIDER", "google"
    )
    monkeypatch.setattr("riskgpt.helpers.search.settings.SEARCH_PROVIDER", "google")
    monkeypatch.setattr("riskgpt.helpers.search.settings.INCLUDE_WIKIPEDIA", True)

    request = SearchRequest(
        query="artificial intelligence", source_type=TopicEnum.LINKEDIN, max_results=5
    )
    response = await search(request)

    assert response.success is True
    assert len(response.results) > 0

    # Check if we have both Google and Wikipedia results
    has_wikipedia = False
    has_google = False

    for result in response.results:
        if "wikipedia.org" in result.url:
            has_wikipedia = True
        else:
            has_google = True

    assert has_wikipedia, "No Wikipedia results found"
    assert has_google, "No Google results found"


@pytest.fixture
def mock_settings(monkeypatch) -> Generator[None, None, None]:
    """Fixture to patch the settings to use tavily as the search provider."""
    monkeypatch.setattr(
        "riskgpt.helpers.search.factory.settings.SEARCH_PROVIDER", "tavily"
    )
    monkeypatch.setattr("riskgpt.helpers.search.settings.SEARCH_PROVIDER", "tavily")
    monkeypatch.setattr("riskgpt.helpers.search.settings.INCLUDE_WIKIPEDIA", False)
    yield


@pytest.fixture
def search_request() -> SearchRequest:
    """Fixture to create a SearchRequest object."""
    return SearchRequest(query="test query", source_type=TopicEnum.NEWS, max_results=5)


# Fixtures for mocking search functions
@pytest.fixture
def mock_google_search() -> SearchResponse:
    """Fixture to mock Google search function."""
    return SearchResponse(
        results=[
            SearchResult(
                title="G",
                url="u",
                date="",
                type="news",
                content="c",
                score=1.0,
            )
        ],
        success=True,
        error_message="",
    )


@pytest.fixture
def mock_wikipedia_search() -> SearchResponse:
    """Fixture to mock Wikipedia search function."""
    return SearchResponse(
        results=[
            SearchResult(
                title="W",
                url="u",
                date="",
                type="news",
                content="c",
                score=0.8,  # Lower score for Wikipedia
            )
        ],
        success=True,
        error_message="",
    )


@pytest.fixture
def mock_duckduckgo_search() -> SearchResponse:
    """Fixture to mock DuckDuckGo search function."""
    return SearchResponse(
        results=[
            SearchResult(
                title="D",
                url="u",
                date="",
                type="news",
                content="c",
                score=1.0,
            )
        ],
        success=True,
        error_message="",
    )


@pytest.mark.asyncio
async def test_search_google_with_mock(
    monkeypatch,
    search_request: SearchRequest,
    mock_google_search: SearchResponse,
    mock_wikipedia_search: SearchResponse,
) -> None:
    """Search using mocked Google provider."""
    # Set up the test environment
    monkeypatch.setattr(
        "riskgpt.helpers.search.factory.settings.SEARCH_PROVIDER", "google"
    )
    monkeypatch.setattr("riskgpt.helpers.search.settings.SEARCH_PROVIDER", "google")

    # Create mock provider
    mock_google_provider = MagicMock()
    mock_google_provider.search.return_value = mock_google_search

    # Test with Google provider
    with patch(
        "riskgpt.helpers.search.get_search_provider", return_value=mock_google_provider
    ):
        # Mock the _execute_search function to return the mock_google_search
        with patch(
            "riskgpt.helpers.search._execute_search", return_value=mock_google_search
        ):
            search_response = await search(search_request)
            assert search_response.success is True
            assert any(result.title == "G" for result in search_response.results)


@pytest.mark.asyncio
async def test_search_duckduckgo_with_mock(
    monkeypatch,
    search_request: SearchRequest,
    mock_duckduckgo_search: SearchResponse,
    mock_wikipedia_search: SearchResponse,
) -> None:
    """Search using mocked DuckDuckGo provider."""
    # Set up the test environment
    monkeypatch.setattr(
        "riskgpt.helpers.search.factory.settings.SEARCH_PROVIDER", "duckduckgo"
    )
    monkeypatch.setattr("riskgpt.helpers.search.settings.SEARCH_PROVIDER", "duckduckgo")

    # Create mock provider
    mock_duckduckgo_provider = MagicMock()
    mock_duckduckgo_provider.search.return_value = mock_duckduckgo_search

    # Test with DuckDuckGo provider
    with patch(
        "riskgpt.helpers.search.get_search_provider",
        return_value=mock_duckduckgo_provider,
    ):
        # Mock the _execute_search function to return the mock_duckduckgo_search
        with patch(
            "riskgpt.helpers.search._execute_search",
            return_value=mock_duckduckgo_search,
        ):
            search_response = await search(search_request)
            assert search_response.success is True
            assert any(result.title == "D" for result in search_response.results)


@pytest.mark.asyncio
async def test_search_wikipedia_with_mock(
    monkeypatch, search_request: SearchRequest, mock_wikipedia_search: SearchResponse
) -> None:
    """Search using mocked Wikipedia provider."""
    monkeypatch.setattr(
        "riskgpt.helpers.search.factory.settings.SEARCH_PROVIDER", "wikipedia"
    )
    monkeypatch.setattr("riskgpt.helpers.search.settings.SEARCH_PROVIDER", "wikipedia")
    # Use AsyncMock to properly mock the async search method
    mock_search = AsyncMock(return_value=mock_wikipedia_search)
    with patch.object(
        WikipediaSearchProvider,
        "search",
        mock_search,
    ):
        search_response: SearchResponse = await search(search_request)
        assert search_response.success is True
        assert search_response.results[0].title.startswith("W")


@pytest.mark.skipif(
    not os.environ.get("GOOGLE_API_KEY") or not os.environ.get("GOOGLE_CSE_ID"),
    reason="Google API key or CSE ID not set",
)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_combined_search_with_context_aware():
    """Test combined search with context-aware Wikipedia integration.

    This test performs a live search using both the primary provider (Google)
    and Wikipedia with context-aware mode enabled.
    """
    # Set up the test environment for combined search with context-aware Wikipedia
    with (
        patch("riskgpt.helpers.search.settings.INCLUDE_WIKIPEDIA", True),
        patch("riskgpt.helpers.search.settings.WIKIPEDIA_CONTEXT_AWARE", True),
        patch("riskgpt.helpers.search.settings.SEARCH_PROVIDER", "google"),
    ):
        # Create a search request that should include Wikipedia (knowledge query)
        request = SearchRequest(
            query="what is artificial intelligence",
            source_type=TopicEnum.NEWS,
            max_results=3,
        )

        # Perform the search
        response = await search(request)

        # Verify the search was successful
        assert response.success is True

        # Check that we have results
        assert len(response.results) > 0

        # Check if any results are from Wikipedia
        has_wikipedia = any(
            "wikipedia.org" in result.url for result in response.results
        )
        assert has_wikipedia, "No Wikipedia results found in context-aware mode"

        # Print the results for comparison
        print("\nResults with context-aware Wikipedia:")
        for i, result in enumerate(response.results):
            print(f"{i+1}. {result.title} - {result.url}")


@pytest.mark.skipif(
    not os.environ.get("GOOGLE_API_KEY") or not os.environ.get("GOOGLE_CSE_ID"),
    reason="Google API key or CSE ID not set",
)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_combined_search_without_context_aware():
    """Test combined search without context-aware Wikipedia integration.

    This test performs a live search using both the primary provider (Google)
    and Wikipedia with context-aware mode disabled.
    """
    # Set up the test environment for combined search without context-aware Wikipedia
    with (
        patch("riskgpt.helpers.search.settings.INCLUDE_WIKIPEDIA", True),
        patch("riskgpt.helpers.search.settings.WIKIPEDIA_CONTEXT_AWARE", False),
        patch("riskgpt.helpers.search.settings.SEARCH_PROVIDER", "google"),
    ):
        # Create a search request
        request = SearchRequest(
            query="latest developments in AI regulation",
            source_type=TopicEnum.NEWS,
            max_results=3,
        )

        # Perform the search
        response = await search(request)

        # Verify the search was successful
        assert response.success is True

        # Check that we have results
        assert len(response.results) > 0

        # Check if any results are from Wikipedia
        has_wikipedia = any(
            "wikipedia.org" in result.url for result in response.results
        )
        assert has_wikipedia, "No Wikipedia results found with context-aware disabled"

        # Print the results for comparison
        print("\nResults without context-aware Wikipedia:")
        for i, result in enumerate(response.results):
            print(f"{i+1}. {result.title} - {result.url}")


@pytest.mark.skipif(
    not os.environ.get("GOOGLE_API_KEY") or not os.environ.get("GOOGLE_CSE_ID"),
    reason="Google API key or CSE ID not set",
)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_compare_context_aware_modes():
    """Compare search results with and without context-aware Wikipedia.

    This test performs two searches with the same query, one with context-aware
    Wikipedia enabled and one with it disabled, to compare the differences.
    """
    # Use a query that's more likely to show differences between modes
    query = "what is quantum computing"

    # First search with context-aware enabled
    with (
        patch("riskgpt.helpers.search.settings.INCLUDE_WIKIPEDIA", True),
        patch("riskgpt.helpers.search.settings.WIKIPEDIA_CONTEXT_AWARE", True),
        patch("riskgpt.helpers.search.settings.SEARCH_PROVIDER", "google"),
    ):
        request = SearchRequest(query=query, source_type=TopicEnum.NEWS, max_results=5)
        context_aware_response = await search(request)

        assert context_aware_response.success is True
        assert len(context_aware_response.results) > 0

    # Second search with context-aware disabled
    with (
        patch("riskgpt.helpers.search.settings.INCLUDE_WIKIPEDIA", True),
        patch("riskgpt.helpers.search.settings.WIKIPEDIA_CONTEXT_AWARE", False),
        patch("riskgpt.helpers.search.settings.SEARCH_PROVIDER", "google"),
    ):
        request = SearchRequest(query=query, source_type=TopicEnum.NEWS, max_results=5)
        non_context_aware_response = await search(request)

        assert non_context_aware_response.success is True
        assert len(non_context_aware_response.results) > 0

    # Compare the results
    context_aware_urls = set(result.url for result in context_aware_response.results)
    non_context_aware_urls = set(
        result.url for result in non_context_aware_response.results
    )

    # Find common and unique URLs
    common_urls = context_aware_urls.intersection(non_context_aware_urls)
    context_aware_only = context_aware_urls - non_context_aware_urls
    non_context_aware_only = non_context_aware_urls - context_aware_urls

    # Print comparison information
    print(f"\nTotal results with context-aware: {len(context_aware_response.results)}")
    print(
        f"Total results without context-aware: {len(non_context_aware_response.results)}"
    )
    print(f"Common URLs: {len(common_urls)}")
    print(f"URLs only in context-aware: {len(context_aware_only)}")
    print(f"URLs only in non-context-aware: {len(non_context_aware_only)}")

    # Check if Wikipedia is included in either result set
    context_aware_has_wiki = any("wikipedia.org" in url for url in context_aware_urls)
    non_context_aware_has_wiki = any(
        "wikipedia.org" in url for url in non_context_aware_urls
    )

    print(f"Wikipedia included in context-aware results: {context_aware_has_wiki}")
    print(
        f"Wikipedia included in non-context-aware results: {non_context_aware_has_wiki}"
    )

    # Print both result sets for comparison
    print("\nContext-aware results:")
    for i, result in enumerate(context_aware_response.results):
        print(f"{i+1}. {result.title} - {result.url}")

    print("\nNon-context-aware results:")
    for i, result in enumerate(non_context_aware_response.results):
        print(f"{i+1}. {result.title} - {result.url}")

    # The test passes as long as we get results from both modes
    # We don't require them to be different, just report the differences
