"""Tests for the Semantic Scholar search provider."""

from unittest.mock import MagicMock, patch

import pytest

from riskgpt.helpers.search import search
from riskgpt.helpers.search.semantic_scholar import SemanticScholarSearchProvider
from riskgpt.models.enums import TopicEnum
from riskgpt.models.helpers.search import SearchRequest, SearchResponse, SearchResult


@pytest.fixture
def mock_semantic_scholar_response():
    """Fixture to create a mock Semantic Scholar API response."""
    return {
        "data": [
            {
                "title": "Machine Learning Explainability: A Survey",
                "url": "https://example.com/paper1",
                "abstract": "This paper provides a survey of machine learning explainability techniques.",
                "venue": "Journal of AI Research",
                "year": 2023,
                "authors": [
                    {"name": "John Smith"},
                    {"name": "Jane Doe"},
                    {"name": "Bob Johnson"},
                    {"name": "Alice Brown"},
                ],
                "score": 0.95,
            },
            {
                "title": "Explainable AI: Concepts and Applications",
                "url": "https://example.com/paper2",
                "abstract": "This paper explores the concepts and applications of explainable AI.",
                "venue": "Conference on AI",
                "year": 2022,
                "authors": [
                    {"name": "Sarah Wilson"},
                    {"name": "Michael Lee"},
                ],
                "score": 0.85,
            },
        ]
    }


def test_semantic_scholar_search_provider(mock_semantic_scholar_response):
    """Test the Semantic Scholar search provider directly."""
    provider = SemanticScholarSearchProvider()
    request = SearchRequest(
        query="machine learning explainability",
        source_type=TopicEnum.ACADEMIC,
        max_results=2,
    )

    with patch("requests.get") as mock_get:
        # Configure the mock to return a response with the mock data
        mock_response = MagicMock()
        mock_response.json.return_value = mock_semantic_scholar_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        response = provider.search(request)

        assert response.success is True
        assert len(response.results) == 2

        # Check first result
        assert response.results[0].title == "Machine Learning Explainability: A Survey"
        assert response.results[0].url == "https://example.com/paper1"
        assert response.results[0].date == "2023"
        assert response.results[0].type == "academic"
        assert "This paper provides a survey" in response.results[0].content
        assert "John Smith, Jane Doe, Bob Johnson et al." in response.results[0].content

        # Check second result
        assert response.results[1].title == "Explainable AI: Concepts and Applications"
        assert response.results[1].url == "https://example.com/paper2"
        assert response.results[1].date == "2022"
        assert response.results[1].type == "academic"
        assert "This paper explores the concepts" in response.results[1].content
        assert "Sarah Wilson, Michael Lee" in response.results[1].content


def test_semantic_scholar_search_with_factory():
    """Test that the factory correctly returns the Semantic Scholar provider."""
    with patch(
        "riskgpt.helpers.search.factory.settings.SEARCH_PROVIDER", "semantic_scholar"
    ):
        from riskgpt.helpers.search.factory import get_search_provider

        provider = get_search_provider()
        assert isinstance(provider, SemanticScholarSearchProvider)


def test_academic_search_excludes_wikipedia():
    """Test that academic searches exclude Wikipedia results."""
    # Mock the primary provider (Semantic Scholar)
    mock_semantic_scholar = MagicMock()
    mock_semantic_scholar.__class__.__name__ = "SemanticScholarSearchProvider"
    mock_semantic_scholar.search.return_value = SearchResponse(
        results=[SearchResult(title="Academic Paper", url="https://example.com/paper")],
        success=True,
    )

    # Mock the Wikipedia provider
    mock_wikipedia = MagicMock()
    mock_wikipedia.__class__.__name__ = "WikipediaSearchProvider"

    with (
        patch(
            "riskgpt.helpers.search.get_search_provider",
            return_value=mock_semantic_scholar,
        ),
        patch(
            "riskgpt.helpers.search.WikipediaSearchProvider",
            return_value=mock_wikipedia,
        ),
        patch("riskgpt.helpers.search.settings.INCLUDE_WIKIPEDIA", True),
        patch("riskgpt.helpers.search.settings.WIKIPEDIA_CONTEXT_AWARE", False),
        patch("riskgpt.helpers.search.settings.SEARCH_PROVIDER", "semantic_scholar"),
    ):
        request = SearchRequest(
            query="machine learning explainability",
            source_type=TopicEnum.ACADEMIC,
            max_results=5,
        )

        search(request)

        # Verify that the primary provider was called
        mock_semantic_scholar.search.assert_called_once()

        # Verify that the Wikipedia provider was NOT called
        mock_wikipedia.search.assert_not_called()


@pytest.mark.integration
def test_semantic_scholar_live():
    """Test the Semantic Scholar search provider with a live API call.

    This test is marked as integration and will be skipped unless run explicitly.
    """
    provider = SemanticScholarSearchProvider()
    request = SearchRequest(
        query="machine learning explainability",
        source_type=TopicEnum.ACADEMIC,
        max_results=2,
    )

    response = provider.search(request)

    assert response.success is True
    assert len(response.results) > 0

    for result in response.results:
        assert result.title
        assert result.url
        assert result.type == "academic"
        assert result.content
