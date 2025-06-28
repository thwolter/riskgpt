from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from riskgpt.helpers.search import _should_include_wikipedia, search
from riskgpt.helpers.search.utils import deduplicate_results, rank_results
from riskgpt.models.enums import TopicEnum
from riskgpt.models.helpers.search import SearchRequest, SearchResponse, SearchResult


class TestDeduplication:
    """Test the deduplication functionality."""

    def test_deduplicate_exact_url(self):
        """Test deduplication of results with exact same URLs."""
        results = [
            SearchResult(
                title="Result 1", url="http://example.com", content="Content 1"
            ),
            SearchResult(
                title="Result 2", url="http://example.com", content="Content 2"
            ),
            SearchResult(title="Result 3", url="http://other.com", content="Content 3"),
        ]

        deduplicated = deduplicate_results(results)

        # Should only have 2 results after deduplication
        assert len(deduplicated) == 2
        assert deduplicated[0].url == "http://example.com"
        assert deduplicated[1].url == "http://other.com"

    def test_deduplicate_similar_url(self):
        """Test deduplication of results with similar URLs."""
        results = [
            SearchResult(
                title="Result 1", url="http://example.com", content="Content 1"
            ),
            SearchResult(
                title="Result 2", url="http://example.com/", content="Content 2"
            ),
            SearchResult(
                title="Result 3", url="http://EXAMPLE.COM", content="Content 3"
            ),
        ]

        deduplicated = deduplicate_results(results)

        # Should only have 1 result after deduplication
        assert len(deduplicated) == 1
        assert deduplicated[0].url.lower().rstrip("/") == "http://example.com"

    def test_deduplicate_content_similarity(self):
        """Test deduplication based on content similarity."""
        # Create results with titles where one is a substring of the other
        results = [
            SearchResult(
                title="Artificial Intelligence",
                url="http://example1.com",
                content="Artificial intelligence is a branch of computer science that aims to create systems capable of performing tasks that normally require human intelligence.",
            ),
            SearchResult(
                title="Introduction to Artificial Intelligence",
                url="http://example2.com",
                content="Artificial intelligence is a branch of computer science that aims to create systems capable of performing tasks that normally require human intelligence.",
            ),
            SearchResult(
                title="Something completely different",
                url="http://example3.com",
                content="This content is not related to AI at all.",
            ),
        ]

        deduplicated = deduplicate_results(results)

        # Should have 2 results after deduplication (the first two are similar)
        assert len(deduplicated) == 2
        # Either the first or second result should be kept, but not both
        assert (
            len(
                [
                    r
                    for r in deduplicated
                    if r.url in ["http://example1.com", "http://example2.com"]
                ]
            )
            == 1
        )
        # The third result should always be kept
        assert any(r.url == "http://example3.com" for r in deduplicated)


class TestRanking:
    """Test the ranking functionality."""

    def test_ranking_by_source_type(self):
        """Test ranking results by source type."""
        results = [
            SearchResult(title="News", url="http://news.com", type="news", score=1.0),
            SearchResult(
                title="Regulatory", url="http://reg.com", type="regulatory", score=1.0
            ),
            SearchResult(
                title="Professional",
                url="http://prof.com",
                type="professional",
                score=1.0,
            ),
            SearchResult(title="Peer", url="http://peer.com", type="peer", score=1.0),
        ]

        ranked = rank_results(results)

        # Regulatory should be first (highest weight)
        assert ranked[0].type == "regulatory"
        # News and Professional should be next (equal weight)
        assert ranked[1].type in ["news", "professional"]
        assert ranked[2].type in ["news", "professional"]
        # Peer should be last
        assert ranked[3].type == "peer"

    def test_ranking_wikipedia(self):
        """Test ranking with Wikipedia results."""
        results = [
            SearchResult(title="News", url="http://news.com", type="news", score=1.0),
            SearchResult(
                title="Wiki",
                url="http://wikipedia.org/wiki/Test",
                type="news",
                score=1.0,
            ),
        ]

        ranked = rank_results(results)

        # News should be ranked higher than Wikipedia
        assert ranked[0].url == "http://news.com"
        assert ranked[1].url == "http://wikipedia.org/wiki/Test"


class TestContextualWikipedia:
    """Test the contextual Wikipedia inclusion."""

    def test_knowledge_query_inclusion(self):
        """Test that knowledge queries include Wikipedia."""
        request = SearchRequest(
            query="what is artificial intelligence", source_type=TopicEnum.NEWS
        )
        assert _should_include_wikipedia(request) is True

        request = SearchRequest(
            query="explain quantum computing", source_type=TopicEnum.NEWS
        )
        assert _should_include_wikipedia(request) is True

    def test_regulatory_inclusion(self):
        """Test that regulatory queries include Wikipedia."""
        request = SearchRequest(
            query="GDPR compliance", source_type=TopicEnum.REGULATORY
        )
        assert _should_include_wikipedia(request) is True

    def test_news_exclusion(self):
        """Test that recent news queries exclude Wikipedia."""
        request = SearchRequest(
            query="latest tech news today", source_type=TopicEnum.NEWS
        )
        assert _should_include_wikipedia(request) is False

        request = SearchRequest(query="breaking news on AI", source_type=TopicEnum.NEWS)
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
            results=[SearchResult(title="Primary Result")], success=True
        )
    )

    wiki_provider = MagicMock()
    wiki_provider.search = AsyncMock(
        return_value=SearchResponse(
            results=[SearchResult(title="Wiki Result")], success=True
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
        request = SearchRequest(query=query, source_type=TopicEnum.NEWS)
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
        results=[SearchResult(title="Test Result")], success=True
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
    request = SearchRequest(query="test query", source_type=TopicEnum.NEWS)
    result = await search(request)

    # Verify the search was successful
    assert result.success is True

    # Verify _execute_search was called twice (once for each provider)
    assert mock_execute_search.call_count == 2

    # Verify it was called with the correct providers
    calls = mock_execute_search.call_args_list
    assert calls[0][0][0] == mock_provider
    assert calls[1][0][0] == mock_wiki
