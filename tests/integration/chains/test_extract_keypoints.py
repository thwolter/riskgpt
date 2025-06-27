"""
test_extract_keypoints.py

This module contains both unit and integration tests for the `extract_key_points` function from the `riskgpt.chains.extract_keypoints` module.
The tests focus on verifying correct extraction of key points from different source types.

Key Components:
---------------
- Unit tests:
    - test_extract_key_points_news: Tests extracting key points from a news source with mocked LLM
    - test_extract_key_points_research: Tests extracting key points from a research source with mocked LLM
    - test_extract_key_points_from_source: Tests creating a request from a Source object with mocked LLM

- Integration tests:
    - test_extract_key_points_integration: Tests the full chain with a real LLM call

Dependencies:
-------------
- pytest (with asyncio support)
- riskgpt.chains.extract_keypoints.extract_key_points
- riskgpt.models.workflows.context.ExtractKeyPointsRequest
- riskgpt.models.workflows.context.ExtractKeyPointsResponse
- riskgpt.models.workflows.context.KeyPoint
- riskgpt.models.enums.TopicEnum
"""

import logging
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from riskgpt.chains.extract_keypoints import extract_key_points
from riskgpt.logger import configure_logging
from riskgpt.models.base import ResponseInfo
from riskgpt.models.enums import TopicEnum
from riskgpt.models.workflows.context import (
    ExtractKeyPointsRequest,
    ExtractKeyPointsResponse,
    KeyPoint,
)


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
                topic=TopicEnum.NEWS,
                source_url="https://example.com/news1",
            ),
            KeyPoint(
                content="Key point 2 about finance",
                topic=TopicEnum.REGULATORY,
                source_url="https://example.com/news1",
            ),
        ],
        response_info=ResponseInfo(
            consumed_tokens=100,
            total_cost=0.002,
            prompt_name="extract_NEWS_key_points",
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
            source_type="NEWS",
            content="Title: Test News Article\n\nContent: This is a test news article about technology and finance.",
        )

        # Call the function under test
        result = await extract_key_points(request)

        # Verify the result
        assert isinstance(result, ExtractKeyPointsResponse)
        assert len(result.points) == 2
        assert result.points[0].content == "Key point 1 about technology"
        assert result.points[0].topic == TopicEnum.NEWS
        assert result.points[1].content == "Key point 2 about finance"
        assert result.points[1].topic == TopicEnum.REGULATORY
        assert result.response_info.prompt_name == "extract_NEWS_key_points"

        # Verify that the chain was invoked with the correct inputs
        mock_chain.invoke.assert_called_once()
        call_args = mock_chain.invoke.call_args[0][0]
        assert call_args["source_type"] == "NEWS"
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
                topic=TopicEnum.PEER,
                source_url="https://example.com/research1",
            ),
            KeyPoint(
                content="Research finding 2",
                topic=TopicEnum.PEER,
                source_url="https://example.com/research1",
            ),
        ],
        response_info=ResponseInfo(
            consumed_tokens=120,
            total_cost=0.0024,
            prompt_name="extract_RESEARCH_key_points",
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
            source_type="RESEARCH",
            content="Title: Research Paper\n\nContent: This is a test research paper with important findings.",
        )

        # Call the function under test
        result = await extract_key_points(request)

        # Verify the result
        assert isinstance(result, ExtractKeyPointsResponse)
        assert len(result.points) == 2
        assert result.points[0].content == "Research finding 1"
        assert result.points[0].topic == TopicEnum.PEER
        assert result.points[1].content == "Research finding 2"
        assert result.points[1].topic == TopicEnum.PEER
        assert result.response_info.prompt_name == "extract_RESEARCH_key_points"

        # Verify that the chain was invoked with the correct inputs
        mock_chain.invoke.assert_called_once()
        call_args = mock_chain.invoke.call_args[0][0]
        assert call_args["source_type"] == "RESEARCH"
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
                topic=TopicEnum.NEWS,
                source_url="https://example.com/source1",
            ),
        ],
        response_info=ResponseInfo(
            consumed_tokens=80,
            total_cost=0.0016,
            prompt_name="extract_NEWS_key_points",
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
        mock_source.type = "NEWS"
        mock_source.title = "Source Title"
        mock_source.content = "Source Content"

        # Create a request from the source
        request = ExtractKeyPointsRequest.from_source(mock_source)

        # Call the function under test
        result = await extract_key_points(request)

        # Verify the result
        assert isinstance(result, ExtractKeyPointsResponse)
        assert len(result.points) == 1
        assert result.points[0].content == "Source key point 1"
        assert result.points[0].topic == TopicEnum.NEWS
        assert result.response_info.prompt_name == "extract_NEWS_key_points"

        # Verify that the chain was invoked with the correct inputs
        mock_chain.invoke.assert_called_once()
        call_args = mock_chain.invoke.call_args[0][0]
        assert call_args["source_type"] == "NEWS"
        assert "content" in call_args
        assert "Title: Source Title" in call_args["content"]
        assert "Content: Source Content" in call_args["content"]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_extract_key_points_integration():
    """Integration test for extract_key_points with a real LLM call."""
    # Create a test request with sample content
    request = ExtractKeyPointsRequest(
        source_type="NEWS",
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
    result = await extract_key_points(request)

    # Verify the structure of the response
    assert isinstance(result, ExtractKeyPointsResponse)
    assert isinstance(result.points, list)
    assert len(result.points) > 0

    # Check that each key point has the expected structure
    for point in result.points:
        assert isinstance(point, KeyPoint)
        assert isinstance(point.content, str)
        assert len(point.content) > 0
        assert isinstance(point.topic, TopicEnum)

    # Verify response info
    assert result.response_info is not None
    assert result.response_info.consumed_tokens > 0
    assert result.response_info.prompt_name == "extract_NEWS_key_points"
