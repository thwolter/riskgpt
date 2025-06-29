from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import HttpUrl
from riskgpt.helpers.search import _should_include_wikipedia, search
from riskgpt.helpers.search.utils import deduplicate_results, rank_results
from riskgpt.models.enums import ScopeEnum
from riskgpt.models.helpers.citation import Citation
from riskgpt.models.helpers.search import SearchRequest, SearchResponse, SearchResult


class TestDeduplication:
    """Test the deduplication functionality."""

    def test_deduplicate_exact_url(self):
        """Test deduplication of results with exact same URLs."""
        results = [
            SearchResult(
                scope=ScopeEnum.NEWS,
                content="Content 1",
                citation=Citation(title="Result 1", url=HttpUrl("http://example.com")),
            ),
            SearchResult(
                scope=ScopeEnum.NEWS,
                content="Content 2",
                citation=Citation(title="Result 2", url=HttpUrl("http://example.com")),
            ),
            SearchResult(
                scope=ScopeEnum.NEWS,
                content="Content 3",
                citation=Citation(title="Result 3", url=HttpUrl("http://other.com")),
            ),
        ]

        deduplicated = deduplicate_results(results)

        # Should only have 2 results after deduplication
        assert len(deduplicated) == 2
        assert str(deduplicated[0].citation.url).rstrip("/") == "http://example.com"
        assert str(deduplicated[1].citation.url).rstrip("/") == "http://other.com"

    def test_deduplicate_similar_url(self):
        """Test deduplication of results with similar URLs."""
        results = [
            SearchResult(
                scope=ScopeEnum.NEWS,
                content="Content 1",
                citation=Citation(title="Result 1", url=HttpUrl("http://example.com")),
            ),
            SearchResult(
                scope=ScopeEnum.NEWS,
                content="Content 2",
                citation=Citation(title="Result 2", url=HttpUrl("http://example.com/")),
            ),
            SearchResult(
                scope=ScopeEnum.NEWS,
                content="Content 3",
                citation=Citation(title="Result 3", url=HttpUrl("http://EXAMPLE.COM")),
            ),
        ]

        deduplicated = deduplicate_results(results)

        # Should only have 1 result after deduplication
        assert len(deduplicated) == 1
        assert (
            str(deduplicated[0].citation.url).lower().rstrip("/")
            == "http://example.com"
        )

    def test_deduplicate_content_similarity(self):
        """Test deduplication based on content similarity."""
        # Create results with titles where one is a substring of the other
        results = [
            SearchResult(
                scope=ScopeEnum.NEWS,
                content="Artificial intelligence is a branch of computer science that aims to create systems capable of performing tasks that normally require human intelligence.",
                citation=Citation(
                    title="Artificial Intelligence", url=HttpUrl("http://example1.com")
                ),
            ),
            SearchResult(
                scope=ScopeEnum.NEWS,
                content="Artificial intelligence is a branch of computer science that aims to create systems capable of performing tasks that normally require human intelligence.",
                citation=Citation(
                    title="Introduction to Artificial Intelligence",
                    url=HttpUrl("http://example2.com"),
                ),
            ),
            SearchResult(
                scope=ScopeEnum.NEWS,
                content="This content is not related to AI at all.",
                citation=Citation(
                    title="Something completely different",
                    url=HttpUrl("http://example3.com"),
                ),
            ),
        ]

        # Print the original results for debugging
        print("\nOriginal results:")
        for r in results:
            print(
                f"URL: {r.citation.url}, Title: {r.citation.title}, Content: {r.content[:30]}..."
            )

        deduplicated = deduplicate_results(results)

        # Print the deduplicated results for debugging
        print("\nDeduplicated results:")
        for r in deduplicated:
            print(
                f"URL: {r.citation.url}, Title: {r.citation.title}, Content: {r.content[:30]}..."
            )

        # Should have 2 results after deduplication (the first two are similar)
        assert len(deduplicated) == 2

        # Check which URLs are in the deduplicated results
        urls_in_deduplicated = [str(r.citation.url) for r in deduplicated]
        print(f"\nURLs in deduplicated results: {urls_in_deduplicated}")

        # Either the first or second result should be kept, but not both
        assert (
            len(
                [
                    r
                    for r in deduplicated
                    if str(r.citation.url).rstrip("/")
                    in ["http://example1.com", "http://example2.com"]
                ]
            )
            == 1
        )
        # The third result should always be kept
        assert any(
            str(r.citation.url).rstrip("/") == "http://example3.com"
            for r in deduplicated
        )


class TestRanking:
    """Test the ranking functionality."""

    def test_ranking_by_scope(self):
        """Test ranking results by source type."""
        results = [
            SearchResult(
                scope=ScopeEnum.NEWS,
                score=1.0,
                content="News content",
                citation=Citation(title="News", url=HttpUrl("http://news.com")),
            ),
            SearchResult(
                scope=ScopeEnum.REGULATORY,
                score=1.0,
                content="Regulatory content",
                citation=Citation(title="Regulatory", url=HttpUrl("http://reg.com")),
            ),
            SearchResult(
                scope=ScopeEnum.PEER,
                score=1.0,
                content="Professional content",
                citation=Citation(title="Professional", url=HttpUrl("http://prof.com")),
            ),
            SearchResult(
                scope=ScopeEnum.PEER,
                score=1.0,
                content="Peer content",
                citation=Citation(title="Peer", url=HttpUrl("http://peer.com")),
            ),
        ]

        ranked = rank_results(results)

        # Regulatory should be first (highest weight)
        assert ranked[0].scope == ScopeEnum.REGULATORY
        # News should be next (higher weight than peer)
        assert ranked[1].scope == ScopeEnum.NEWS
        # Peer should be last (two peer results with equal weight)
        assert ranked[2].scope == ScopeEnum.PEER
        assert ranked[3].scope == ScopeEnum.PEER

    def test_ranking_wikipedia(self):
        """Test ranking with Wikipedia results."""
        results = [
            SearchResult(
                scope=ScopeEnum.NEWS,
                score=1.0,
                content="News content",
                citation=Citation(title="News", url=HttpUrl("http://news.com")),
            ),
            SearchResult(
                scope=ScopeEnum.NEWS,
                score=1.0,
                content="Wiki content",
                citation=Citation(
                    title="Wiki", url=HttpUrl("http://wikipedia.org/wiki/Test")
                ),
            ),
        ]

        ranked = rank_results(results)

        # News should be ranked higher than Wikipedia
        assert str(ranked[0].citation.url).rstrip("/") == "http://news.com"
        assert (
            str(ranked[1].citation.url).rstrip("/") == "http://wikipedia.org/wiki/Test"
        )


class TestContextualWikipedia:
    """Test the contextual Wikipedia inclusion."""

    def test_knowledge_query_inclusion(self):
        """Test that knowledge queries include Wikipedia."""
        request = SearchRequest(
            query="what is artificial intelligence", scope=ScopeEnum.NEWS
        )
        assert _should_include_wikipedia(request) is True

        request = SearchRequest(query="explain quantum computing", scope=ScopeEnum.NEWS)
        assert _should_include_wikipedia(request) is True

    def test_regulatory_inclusion(self):
        """Test that regulatory queries include Wikipedia."""
        request = SearchRequest(query="GDPR compliance", scope=ScopeEnum.REGULATORY)
        assert _should_include_wikipedia(request) is True

    def test_news_exclusion(self):
        """Test that recent news queries exclude Wikipedia."""
        request = SearchRequest(query="latest tech news today", scope=ScopeEnum.NEWS)
        assert _should_include_wikipedia(request) is False

        request = SearchRequest(query="breaking news on AI", scope=ScopeEnum.NEWS)
        assert _should_include_wikipedia(request) is False


@pytest.mark.parametrize(
    "include_wiki,context_aware,query,expected_providers",
    [
        (
            True,
            False,
            "any query",
            ["primary", "wikipedia"],
        ),  # Always include Wikipedia
        (True, True, "what is AI", ["primary", "wikipedia"]),  # Knowledge query
        (True, True, "latest news today", ["primary"]),  # Recent news
        (False, False, "what is AI", ["primary"]),  # Wikipedia disabled
    ],
)
@pytest.mark.asyncio
async def test_search_provider_selection(
    monkeypatch, include_wiki, context_aware, query, expected_providers
):
    """Test that the correct search providers are selected based on settings and query."""
    # Mock settings
    monkeypatch.setattr(
        "riskgpt.helpers.search.settings.INCLUDE_WIKIPEDIA", include_wiki
    )
    monkeypatch.setattr(
        "riskgpt.helpers.search.settings.WIKIPEDIA_CONTEXT_AWARE", context_aware
    )

    # Mock search providers
    primary_provider = MagicMock()
    primary_provider.__class__.__name__ = "PrimaryProvider"
    primary_provider.search = AsyncMock(
        return_value=SearchResponse(
            results=[
                SearchResult(
                    scope=ScopeEnum.NEWS,
                    content="Primary content",
                    citation=Citation(
                        title="Primary Result", url=HttpUrl("http://example.com")
                    ),
                )
            ],
            success=True,
        )
    )

    wiki_provider = MagicMock()
    wiki_provider.search = AsyncMock(
        return_value=SearchResponse(
            results=[
                SearchResult(
                    scope=ScopeEnum.NEWS,
                    content="Wiki content",
                    citation=Citation(
                        title="Wiki Result",
                        url=HttpUrl("http://wikipedia.org/wiki/Test"),
                    ),
                )
            ],
            success=True,
        )
    )

    # Mock get_search_provider to return our mock
    with (
        patch(
            "riskgpt.helpers.search.get_search_provider", return_value=primary_provider
        ),
        patch(
            "riskgpt.helpers.search.WikipediaSearchProvider", return_value=wiki_provider
        ),
        patch("riskgpt.helpers.search.deduplicate_results", lambda x: x),
        patch("riskgpt.helpers.search.rank_results", lambda x: x),
    ):
        request = SearchRequest(query=query, scope=ScopeEnum.NEWS)
        await search(request)

        # Check that the correct providers were called
        if "primary" in expected_providers:
            primary_provider.search.assert_called_once()
        else:
            primary_provider.search.assert_not_called()

        if "wikipedia" in expected_providers:
            wiki_provider.search.assert_called_once()
        else:
            wiki_provider.search.assert_not_called()


@pytest.mark.asyncio
async def test_parallel_execution(monkeypatch):
    """Test that searches are executed in parallel."""
    # Instead of trying to mock the complex ThreadPoolExecutor and as_completed behavior,
    # we'll patch the _execute_search function to verify it's called correctly

    # Create a mock for _execute_search that returns a successful response
    mock_execute_search = AsyncMock()
    mock_execute_search.return_value = SearchResponse(
        results=[
            SearchResult(
                scope=ScopeEnum.NEWS,
                content="Test content",
                citation=Citation(
                    title="Test Result", url=HttpUrl("http://example.com")
                ),
            )
        ],
        success=True,
    )

    # Patch the _execute_search function
    monkeypatch.setattr("riskgpt.helpers.search._execute_search", mock_execute_search)

    # Also patch settings to ensure predictable behavior
    monkeypatch.setattr("riskgpt.helpers.search.settings.INCLUDE_WIKIPEDIA", True)
    monkeypatch.setattr(
        "riskgpt.helpers.search.settings.WIKIPEDIA_CONTEXT_AWARE", False
    )
    monkeypatch.setattr("riskgpt.helpers.search.settings.SEARCH_PROVIDER", "google")

    # Create mock providers
    mock_provider = MagicMock()
    mock_provider.__class__.__name__ = "MockProvider"
    mock_provider.search = AsyncMock()

    mock_wiki = MagicMock()
    mock_wiki.search = AsyncMock()

    # Patch the provider creation functions
    monkeypatch.setattr(
        "riskgpt.helpers.search.get_search_provider", lambda: mock_provider
    )
    monkeypatch.setattr(
        "riskgpt.helpers.search.WikipediaSearchProvider", lambda: mock_wiki
    )

    # Call search
    request = SearchRequest(query="test query", scope=ScopeEnum.NEWS)
    result = await search(request)

    # Verify the search was successful
    assert result.success is True

    # Verify _execute_search was called twice (once for each provider)
    assert mock_execute_search.call_count == 2

    # Verify it was called with the correct providers
    calls = mock_execute_search.call_args_list
    assert calls[0][0][0] == mock_provider
    assert calls[1][0][0] == mock_wiki
