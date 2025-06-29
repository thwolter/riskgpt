"""
test_extract_keypoints.py

This module contains tests for the key points extraction functionality:
1. Basic extraction from different source types
2. Citation handling in extracted key points
3. Integration with research workflow

Key Components:
---------------
- Basic extraction tests:
    - test_extract_key_points_news: Tests extracting key points from a news source with mocked LLM
    - test_extract_key_points_research: Tests extracting key points from a research source with mocked LLM
    - test_extract_key_points_from_source: Tests creating a request from a Source object with mocked LLM

- Citation functionality tests:
    - test_extract_scope_key_points_with_citation: Tests extraction with citation information
    - test_extract_scope_key_points_without_citation: Tests extraction without citation information

- Integration tests:
    - test_extract_key_points_integration: Tests the full chain with a real LLM call
    - test_extract_key_points_with_llm: Tests extraction with citation using a real LLM

Dependencies:
-------------
- pytest (with asyncio support)
- riskgpt.chains.extract_keypoints.extract_key_points_chain
- riskgpt.models.chains.keypoints
- riskgpt.models.enums.ScopeEnum
- riskgpt.models.helpers.citation.Citation
- riskgpt.models.helpers.search.Source
- riskgpt.workflows.research.nodes.extract_scope_key_points
"""

import logging
from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from riskgpt.chains.extract_keypoints import extract_key_points_chain
from riskgpt.logger import configure_logging
from riskgpt.models.base import ResponseInfo
from riskgpt.models.chains.keypoints import (
    ExtractKeyPointsRequest,
    ExtractKeyPointsResponse,
    KeyPoint,
)
from riskgpt.models.enums import ScopeEnum
from riskgpt.models.helpers.citation import Citation
from riskgpt.models.helpers.search import Source
from riskgpt.workflows.research.nodes import extract_scope_key_points
from riskgpt.workflows.research.state import State

# SECTION 1: Basic key points extraction tests


@pytest.mark.asyncio
async def test_extract_key_points_news(monkeypatch, caplog):
    """Test extracting key points from a news source."""
    caplog.set_level(logging.INFO, logger="riskgpt")
    configure_logging(level=logging.INFO)

    # Create a mock response
    mock_response = ExtractKeyPointsResponse(
        points=[
            KeyPoint(
                content="Key point 1 about technology",
                source_url="https://example.com/news1",
                scope=ScopeEnum.NEWS,
            ),
            KeyPoint(
                content="Key point 2 about finance",
                source_url="https://example.com/news1",
                scope=ScopeEnum.NEWS,
            ),
        ],
        response_info=ResponseInfo(
            consumed_tokens=100,
            total_cost=0.002,
            prompt_name="extract_news_key_points",
            model_name="gpt-4",
        ),
    )

    # Create a mock for the BaseChain class
    mock_chain = AsyncMock()
    mock_chain.invoke = AsyncMock(return_value=mock_response)

    # Patch the BaseChain constructor to return our mock
    with patch("riskgpt.chains.extract_keypoints.BaseChain", return_value=mock_chain):
        # Create a test request
        request = ExtractKeyPointsRequest(
            scope=ScopeEnum.NEWS,
            content="Title: Test News Article\n\nContent: This is a test news article about technology and finance.",
        )

        # Call the function under test
        result = await extract_key_points_chain(request)

        # Verify the result
        assert isinstance(result, ExtractKeyPointsResponse)
        assert len(result.points) == 2
        assert result.points[0].content == "Key point 1 about technology"
        assert result.points[0].scope == ScopeEnum.NEWS
        assert result.points[1].content == "Key point 2 about finance"
        assert result.points[1].scope == ScopeEnum.NEWS
        assert result.response_info.prompt_name == "extract_news_key_points"

        # Verify that the chain was invoked with the correct inputs
        mock_chain.invoke.assert_called_once()
        call_args = mock_chain.invoke.call_args[0][0]
        assert call_args["scope"] == "news"
        assert "content" in call_args


@pytest.mark.asyncio
async def test_extract_key_points_research(monkeypatch, caplog):
    """Test extracting key points from a research source."""
    caplog.set_level(logging.INFO, logger="riskgpt")
    configure_logging(level=logging.INFO)

    # Create a mock response
    mock_response = ExtractKeyPointsResponse(
        points=[
            KeyPoint(
                content="Research finding 1",
                source_url="https://example.com/research1",
                scope=ScopeEnum.PEER,
            ),
            KeyPoint(
                content="Research finding 2",
                source_url="https://example.com/research1",
                scope=ScopeEnum.PEER,
            ),
        ],
        response_info=ResponseInfo(
            consumed_tokens=120,
            total_cost=0.0024,
            prompt_name="extract_research_key_points",
            model_name="gpt-4",
        ),
    )

    # Create a mock for the BaseChain class
    mock_chain = AsyncMock()
    mock_chain.invoke = AsyncMock(return_value=mock_response)

    # Patch the BaseChain constructor to return our mock
    with patch("riskgpt.chains.extract_keypoints.BaseChain", return_value=mock_chain):
        # Create a test request
        request = ExtractKeyPointsRequest(
            scope=ScopeEnum.ACADEMIC,
            content="Title: Research Paper\n\nContent: This is a test research paper with important findings.",
        )

        # Call the function under test
        result = await extract_key_points_chain(request)

        # Verify the result
        assert isinstance(result, ExtractKeyPointsResponse)
        assert len(result.points) == 2
        assert result.points[0].content == "Research finding 1"
        assert result.points[0].scope == ScopeEnum.PEER
        assert result.points[1].content == "Research finding 2"
        assert result.points[1].scope == ScopeEnum.PEER
        assert result.response_info.prompt_name == "extract_research_key_points"

        # Verify that the chain was invoked with the correct inputs
        mock_chain.invoke.assert_called_once()
        call_args = mock_chain.invoke.call_args[0][0]
        assert call_args["scope"] == "academic"
        assert "content" in call_args


@pytest.mark.asyncio
async def test_extract_key_points_from_source(monkeypatch, caplog):
    """Test creating a request from a Source object and extracting key points."""
    caplog.set_level(logging.INFO, logger="riskgpt")
    configure_logging(level=logging.INFO)

    # Create a mock response
    mock_response = ExtractKeyPointsResponse(
        points=[
            KeyPoint(
                content="Source key point 1",
                scope=ScopeEnum.NEWS,
                source_url="https://example.com/source1",
            ),
        ],
        response_info=ResponseInfo(
            consumed_tokens=80,
            total_cost=0.0016,
            prompt_name="extract_news_key_points",
            model_name="gpt-4",
        ),
    )

    # Create a mock for the BaseChain class
    mock_chain = AsyncMock()
    mock_chain.invoke = AsyncMock(return_value=mock_response)

    # Patch the BaseChain constructor to return our mock
    with patch("riskgpt.chains.extract_keypoints.BaseChain", return_value=mock_chain):
        # Create a mock Source object
        mock_source = MagicMock()
        mock_source.scope = "news"
        mock_source.title = "Source Title"
        mock_source.content = "Source Content"
        mock_source.url = "https://example.com/source1"
        mock_source.citation = None

        # Create a request from the source
        request = ExtractKeyPointsRequest.from_source(mock_source)

        # Call the function under test
        result = await extract_key_points_chain(request)

        # Verify the result
        assert isinstance(result, ExtractKeyPointsResponse)
        assert len(result.points) == 1
        assert result.points[0].content == "Source key point 1"
        assert result.points[0].scope == ScopeEnum.NEWS
        assert result.response_info.prompt_name == "extract_news_key_points"

        # Verify that the chain was invoked with the correct inputs
        mock_chain.invoke.assert_called_once()
        call_args = mock_chain.invoke.call_args[0][0]
        assert call_args["scope"] == "news"
        assert "content" in call_args
        assert "Title: Source Title" in call_args["content"]
        assert "Content: Source Content" in call_args["content"]


# SECTION 2: Citation functionality tests


@pytest.mark.asyncio
async def test_extract_scope_key_points_with_citation():
    """Test extracting key points with citation information."""
    # Create a mock Citation
    citation = Citation(
        url="https://example.com",
        title="Example Paper",
        authors=["John Doe", "Jane Smith"],
        publication_date=date(2023, 1, 1),
        venue="Example Conference",
    )

    # Create a mock Source with citation
    source = Source(
        title="Example Paper",
        url="https://example.com",
        date="2023",
        type="PEER",
        content="This is an example paper content.",
        scope=ScopeEnum.PEER,
        citation=citation,
    )

    # Create a mock State with the source
    state = State(sources=[source])

    # Create a mock ExtractKeyPointsResponse
    mock_response = ExtractKeyPointsResponse(
        points=[
            KeyPoint(
                content="This is key point 1",
                scope=ScopeEnum.PEER,
            ),
            KeyPoint(
                content="This is key point 2",
                scope=ScopeEnum.PEER,
            ),
        ],
    )

    # Mock the extract_key_points_chain function
    with patch(
        "riskgpt.workflows.research.nodes.extract_key_points_chain",
        AsyncMock(return_value=mock_response),
    ):
        # Call the extract_scope_key_points function
        result_state = await extract_scope_key_points(state, ScopeEnum.PEER)

        # Verify that key points were added to the state
        assert "key_points" in result_state
        assert len(result_state["key_points"]) == 2

        # Verify that each key point has the source URL and citation
        for key_point in result_state["key_points"]:
            assert key_point.source_url == "https://example.com"
            assert key_point.citation is not None
            assert key_point.citation == citation

            # Verify that the citation can be formatted
            assert key_point.get_inline_citation() == "John Doe and Jane Smith (2023)"


@pytest.mark.asyncio
async def test_extract_scope_key_points_without_citation():
    """Test extracting key points without citation information."""
    # Create a mock Source without citation
    source = Source(
        title="Example Paper",
        url="https://example.com",
        date="2023",
        type="PEER",
        content="This is an example paper content.",
        scope=ScopeEnum.PEER,
    )

    # Create a mock State with the source
    state = State(sources=[source])

    # Create a mock ExtractKeyPointsResponse
    mock_response = ExtractKeyPointsResponse(
        points=[
            KeyPoint(
                content="This is key point 1",
                scope=ScopeEnum.PEER,
            ),
            KeyPoint(
                content="This is key point 2",
                scope=ScopeEnum.PEER,
            ),
        ],
    )

    # Mock the extract_key_points_chain function
    with patch(
        "riskgpt.workflows.research.nodes.extract_key_points_chain",
        AsyncMock(return_value=mock_response),
    ):
        # Call the extract_scope_key_points function
        result_state = await extract_scope_key_points(state, ScopeEnum.PEER)

        # Verify that key points were added to the state
        assert "key_points" in result_state
        assert len(result_state["key_points"]) == 2

        # Verify that each key point has the source URL but no citation
        for key_point in result_state["key_points"]:
            assert key_point.source_url == "https://example.com"
            assert key_point.citation is None

            # Verify that the inline citation falls back to the URL
            assert key_point.get_inline_citation() == "example.com"


# SECTION 3: Integration tests


@pytest.mark.integration
@pytest.mark.asyncio
async def test_extract_key_points_integration():
    """Integration test for extract_key_points with a real LLM call."""
    # Create a test request with sample content
    request = ExtractKeyPointsRequest(
        scope=ScopeEnum.NEWS,
        content=(
            "Title: AI Advances in Risk Management\n\n"
            "Content: Recent developments in artificial intelligence have shown promising "
            "applications in risk management. Companies are increasingly using AI to identify "
            "potential risks in their operations and to automate risk assessment processes. "
            "However, there are concerns about the reliability and transparency of AI-based "
            "risk management systems. Regulators are starting to pay attention to these issues "
            "and are considering new guidelines for AI use in risk management."
        ),
        focus_keywords=["guidelines"],
    )

    # Call the function under test with a real LLM
    result = await extract_key_points_chain(request)

    # Verify the structure of the response
    assert isinstance(result, ExtractKeyPointsResponse)
    assert isinstance(result.points, list)
    assert len(result.points) > 0

    # Check that each key point has the expected structure
    for point in result.points:
        assert isinstance(point, KeyPoint)
        assert isinstance(point.content, str)
        assert len(point.content) > 0
        assert isinstance(point.scope, ScopeEnum)

    # Verify response info
    assert result.response_info is not None
    assert result.response_info.consumed_tokens > 0
    assert result.response_info.prompt_name == "extract_news_key_points"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_extract_key_points_with_llm():
    """Integration test for extract_key_points with citation using a real LLM."""
    # Create a Citation
    citation = Citation(
        url="https://example.com",
        title="AI Safety Research Paper",
        authors=["John Doe", "Jane Smith"],
        publication_date=date(2023, 1, 1),
        venue="AI Safety Conference",
    )

    # Create a Source with citation
    source = Source(
        title="AI Safety Research Paper",
        url="https://example.com",
        date="2023",
        content=(
            "AI safety is a critical concern as artificial intelligence systems become more powerful. "
            "Researchers have identified several key risks including alignment problems, "
            "where AI systems might optimize for goals that don't align with human values. "
            "Another concern is the potential for unintended consequences when deploying "
            "complex AI systems in real-world environments."
        ),
        scope=ScopeEnum.ACADEMIC,
        citation=citation,
    )

    # Create an ExtractKeyPointsRequest from the Source
    request = ExtractKeyPointsRequest.from_source(source)

    # Call extract_key_points_chain directly with the request
    response = await extract_key_points_chain(request)

    # Verify the response
    assert isinstance(response, ExtractKeyPointsResponse)
    assert len(response.points) > 0

    # Verify response_info is present
    assert response.response_info is not None
    assert response.response_info.consumed_tokens > 0
    assert response.response_info.model_name is not None

    # Verify the content of the key points
    for point in response.points:
        assert point.content
        assert point.scope == ScopeEnum.ACADEMIC

        # Verify that each key point has the source URL and citation
        assert point.source_url == "https://example.com"
        assert point.citation is not None
        assert point.citation == citation

        # Verify that the citation can be formatted
        assert point.get_inline_citation() == "John Doe and Jane Smith (2023)"
