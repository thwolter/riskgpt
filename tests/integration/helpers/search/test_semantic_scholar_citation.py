from datetime import date
from unittest.mock import AsyncMock

import pytest
from riskgpt.helpers.search.semantic_scholar import SemanticScholarSearchProvider
from riskgpt.models.enums import TopicEnum
from riskgpt.models.helpers.citation import Citation
from riskgpt.models.helpers.search import SearchRequest


@pytest.mark.asyncio
async def test_semantic_scholar_creates_citation():
    # Mock API response
    mock_response = {
        "data": [
            {
                "title": "Example Paper",
                "url": "https://example.com/paper",
                "year": 2023,
                "venue": "Example Conference",
                "authors": [
                    {"name": "John Doe"},
                    {"name": "Jane Smith"},
                ],
                "abstract": "This is an example abstract.",
                "score": 0.95,
            }
        ]
    }

    # Create provider and mock the _fetch_with_retry method
    provider = SemanticScholarSearchProvider()
    provider._fetch_with_retry = AsyncMock(return_value=mock_response)

    # Create search request
    request = SearchRequest(
        query="example query",
        source_type=TopicEnum.PEER,
        max_results=1,
    )

    # Execute search
    response = await provider.search(request)

    # Verify response
    assert response.success
    assert len(response.results) == 1

    # Verify citation in result
    result = response.results[0]
    assert result.citation is not None
    assert isinstance(result.citation, Citation)

    # Verify citation fields
    citation = result.citation
    assert citation.url == "https://example.com/paper"
    assert citation.title == "Example Paper"
    assert citation.authors == ["John Doe", "Jane Smith"]
    assert citation.publication_date == date(2023, 1, 1)
    assert citation.venue == "Example Conference"

    # Verify citation formatting
    assert citation.format_harvard_citation() == "John Doe and Jane Smith (2023)"
    assert (
        "John Doe and Jane Smith (2023). Example Paper. Example Conference."
        in citation.format_harvard_reference()
    )
    assert (
        "Available at: https://example.com/paper" in citation.format_harvard_reference()
    )


@pytest.mark.asyncio
async def test_semantic_scholar_handles_missing_fields():
    # Mock API response with missing fields
    mock_response = {
        "data": [
            {
                "title": "Example Paper",
                "url": "https://example.com/paper",
                # No year
                # No venue
                "authors": [],  # Empty authors
                "abstract": "This is an example abstract.",
                "score": 0.95,
            }
        ]
    }

    # Create provider and mock the _fetch_with_retry method
    provider = SemanticScholarSearchProvider()
    provider._fetch_with_retry = AsyncMock(return_value=mock_response)

    # Create search request
    request = SearchRequest(
        query="example query",
        source_type=TopicEnum.PEER,
        max_results=1,
    )

    # Execute search
    response = await provider.search(request)

    # Verify response
    assert response.success
    assert len(response.results) == 1

    # Verify citation in result
    result = response.results[0]
    assert result.citation is not None
    assert isinstance(result.citation, Citation)

    # Verify citation fields
    citation = result.citation
    assert citation.url == "https://example.com/paper"
    assert citation.title == "Example Paper"
    assert citation.authors == []
    assert citation.publication_date is None
    assert citation.venue is None

    # Verify citation formatting
    assert citation.format_harvard_citation() == "example.com"
    assert "example.com. Example Paper." in citation.format_harvard_reference()
    assert (
        "Available at: https://example.com/paper" in citation.format_harvard_reference()
    )
