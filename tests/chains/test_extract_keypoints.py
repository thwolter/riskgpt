from datetime import date
from unittest.mock import AsyncMock, patch

import pytest
from pydantic import HttpUrl

from riskgpt.chains.extract_keypoints import extract_key_points_chain
from riskgpt.models.chains.keypoints import (
    ExtractKeyPointsRequest,
    ExtractKeyPointsResponse,
    KeyPoint,
)
from riskgpt.models.enums import ScopeEnum
from riskgpt.models.helpers.citation import Citation


class TestExtractKeypoints:
    """
    Tests for the key points extraction chain.

    This class tests the functionality of extracting key points from different sources,
    including news and academic sources, with various scenarios.
    """

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "scope,expected_prompt_name",
        [
            (ScopeEnum.NEWS, "extract_news_key_points"),
            (ScopeEnum.ACADEMIC, "extract_research_key_points"),
            (ScopeEnum.PEER, "extract_research_key_points"),
            (ScopeEnum.LINKEDIN, "extract_linkedin_key_points"),
        ],
    )
    async def test_extract_key_points_by_scope(
        self,
        scope,
        expected_prompt_name,
        mock_chain,
        complete_citation,
        configure_test_logging,
        sample_response_info,
    ):
        """Test extracting key points from sources with different scopes."""
        # Configure mock response based on scope
        mock_response = ExtractKeyPointsResponse(
            points=[
                KeyPoint(
                    content=f"Key point 1 for {scope.value}",
                    scope=scope,
                    citation=complete_citation,
                ),
                KeyPoint(
                    content=f"Key point 2 for {scope.value}",
                    scope=scope,
                    citation=complete_citation,
                ),
            ],
            response_info=sample_response_info(expected_prompt_name),
        )

        mock_chain.invoke = AsyncMock(return_value=mock_response)

        # Patch the BaseChain constructor to return our mock
        with patch(
            "riskgpt.chains.extract_keypoints.BaseChain", return_value=mock_chain
        ):
            # Create a test request
            request = ExtractKeyPointsRequest(
                scope=scope,
                content=f"Test {scope.value}:\n\nThis is test content for {scope.value}.",
                citation=complete_citation,
            )

            # Call the function under test
            result = await extract_key_points_chain(request)

            # Verify the result
            assert isinstance(result, ExtractKeyPointsResponse)
            assert len(result.points) == 2
            assert result.points[0].content == f"Key point 1 for {scope.value}"
            assert result.points[0].scope == scope
            assert result.points[1].content == f"Key point 2 for {scope.value}"
            assert result.points[1].scope == scope
            assert result.response_info.prompt_name == expected_prompt_name
            assert result.response_info.error is None

            # Verify that the chain was invoked with the correct inputs
            mock_chain.invoke.assert_called_once()
            call_args = mock_chain.invoke.call_args[0][0]
            assert call_args["scope"] == scope.value.lower()
            assert "content" in call_args

    @pytest.mark.asyncio
    async def test_extract_key_points_from_source(
        self,
        mock_chain,
        news_source,
        mock_news_keypoints_response,
        configure_test_logging,
    ):
        """Test creating a request from a Source object and extracting key points."""
        mock_chain.invoke = AsyncMock(return_value=mock_news_keypoints_response)

        # Patch the BaseChain constructor to return our mock
        with patch(
            "riskgpt.chains.extract_keypoints.BaseChain", return_value=mock_chain
        ):
            # Create a request from the source
            request = ExtractKeyPointsRequest.from_source(news_source)

            # Call the function under test
            result = await extract_key_points_chain(request)

            # Verify the result
            assert isinstance(result, ExtractKeyPointsResponse)
            assert len(result.points) == 2
            assert result.points[0].content == "Key point 1 about technology"
            assert result.points[0].scope == ScopeEnum.NEWS
            assert result.response_info.prompt_name == "extract_news_key_points"
            assert result.response_info.error is None

            # Verify that the chain was invoked with the correct inputs
            mock_chain.invoke.assert_called_once()
            call_args = mock_chain.invoke.call_args[0][0]
            assert call_args["scope"] == "news"
            assert "content" in call_args
            assert news_source.citation.title in call_args["content"]
            assert news_source.content in call_args["content"]

    @pytest.mark.asyncio
    async def test_extract_key_points_with_focus_keywords(
        self,
        mock_chain,
        complete_citation,
        configure_test_logging,
        sample_response_info,
    ):
        """Test extracting key points with focus keywords."""
        # Create a mock response
        mock_response = ExtractKeyPointsResponse(
            points=[
                KeyPoint(
                    content="Key point about technology",
                    scope=ScopeEnum.NEWS,
                    citation=complete_citation,
                ),
            ],
            response_info=sample_response_info("extract_news_key_points"),
        )

        mock_chain.invoke = AsyncMock(return_value=mock_response)

        # Patch the BaseChain constructor to return our mock
        with patch(
            "riskgpt.chains.extract_keypoints.BaseChain", return_value=mock_chain
        ):
            # Create a test request with focus keywords
            request = ExtractKeyPointsRequest(
                scope=ScopeEnum.NEWS,
                content="Title: Test News Article\n\nContent: This is a test news article about technology and finance.",
                citation=complete_citation,
                focus_keywords=["technology", "innovation"],
            )

            # Call the function under test
            result = await extract_key_points_chain(request)

            # Verify the result
            assert isinstance(result, ExtractKeyPointsResponse)
            assert len(result.points) == 1
            assert "technology" in result.points[0].content

            # Verify that the chain was invoked with the correct inputs
            mock_chain.invoke.assert_called_once()
            call_args = mock_chain.invoke.call_args[0][0]
            assert "focus_keywords" in call_args
            assert call_args["focus_keywords"] == ["technology", "innovation"]

    @pytest.mark.asyncio
    async def test_extract_key_points_with_invalid_input(
        self, mock_chain, configure_test_logging, sample_response_info
    ):
        """Test extracting key points with invalid input."""
        # Create a mock response with an error
        mock_response = ExtractKeyPointsResponse(
            points=[],
            response_info=sample_response_info(
                "extract_news_key_points", "Invalid input: content is empty"
            ),
        )

        mock_chain.invoke = AsyncMock(return_value=mock_response)

        # Patch the BaseChain constructor to return our mock
        with patch(
            "riskgpt.chains.extract_keypoints.BaseChain", return_value=mock_chain
        ):
            # Create a test request with empty content
            request = ExtractKeyPointsRequest(
                scope=ScopeEnum.NEWS,
                content="",
                citation=Citation(url=HttpUrl("https://example.com")),
            )

            # Call the function under test
            result = await extract_key_points_chain(request)

            # Verify the result
            assert isinstance(result, ExtractKeyPointsResponse)
            assert len(result.points) == 0
            assert result.response_info.error is not None
            assert "Invalid input" in result.response_info.error

    @pytest.mark.asyncio
    async def test_extract_key_points_with_logging(
        self, mock_chain, configure_test_logging, sample_response_info
    ):
        """Test that key points extraction logs appropriate information."""
        caplog = configure_test_logging

        # Create a mock response
        mock_response = ExtractKeyPointsResponse(
            points=[
                KeyPoint(
                    content="This is a test key point for logging verification.",
                    scope=ScopeEnum.NEWS,
                    citation=Citation(url=HttpUrl("https://example.com/logging-test")),
                ),
            ],
            response_info=sample_response_info(),
        )

        mock_chain.invoke = AsyncMock(return_value=mock_response)

        # Patch the BaseChain constructor to return our mock
        with patch(
            "riskgpt.chains.extract_keypoints.BaseChain", return_value=mock_chain
        ):
            # Create a test request
            request = ExtractKeyPointsRequest(
                scope=ScopeEnum.NEWS,
                content="Title: Test Article\n\nContent: This is a test article for logging verification.",
                citation=Citation(url=HttpUrl("https://example.com/logging-test")),
            )

            # Call the function under test
            result = await extract_key_points_chain(request)

            # Verify the result
            assert isinstance(result, ExtractKeyPointsResponse)
            assert len(result.points) > 0
            assert result.response_info is not None
            assert result.response_info.error is None

            # If there was an error, it should be logged
            if result.response_info.error:
                assert any(
                    result.response_info.error in record.message
                    for record in caplog.records
                )


class TestCitationMerging:
    """
    Tests for citation merging in key points extraction.

    This class tests how citations from the request are merged with citations
    in the key points, handling various scenarios like complete citations,
    partial citations, and conflicting data.
    """

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "keypoint_citation,expected_merged",
        [
            # Case 1: Key point with complete citation should keep its citation
            (
                {
                    "url": "https://example.com/complete",
                    "title": "Complete Title",
                    "authors": ["Complete Author"],
                    "publication_date": date(2023, 2, 2),
                    "venue": "Complete Venue",
                    "publisher": "Complete Publisher",
                },
                {
                    "url": "https://example.com/complete",
                    "title": "Complete Title",
                    "authors": ["Complete Author"],
                    "publication_date": date(2023, 2, 2),
                    "venue": "Complete Venue",
                    "publisher": "Complete Publisher",
                },
            ),
            # Case 2: Key point with partial citation should merge with request citation
            (
                {
                    "url": "https://example.com/partial",
                    "title": "Partial Title",
                },
                {
                    "url": "https://example.com/partial",
                    "title": "Partial Title",
                    "authors": ["Request Author"],
                    "publication_date": date(2023, 1, 1),
                    "venue": "Request Venue",
                    "publisher": "Request Publisher",
                },
            ),
            # Case 3: Key point with minimal citation should merge with request citation
            (
                {
                    "url": "https://example.com/minimal",
                },
                {
                    "url": "https://example.com/minimal",
                    "title": "Request Title",
                    "authors": ["Request Author"],
                    "publication_date": date(2023, 1, 1),
                    "venue": "Request Venue",
                    "publisher": "Request Publisher",
                },
            ),
        ],
    )
    async def test_citation_merging(
        self, keypoint_citation, expected_merged, mock_chain, configure_test_logging
    ):
        """Test citation merging with different citation scenarios."""
        # Create request citation
        request_citation = Citation(
            url=HttpUrl("https://example.com/request"),
            title="Request Title",
            authors=["Request Author"],
            publication_date=date(2023, 1, 1),
            venue="Request Venue",
            publisher="Request Publisher",
        )

        # Create keypoint citation from the test data
        kp_citation = Citation(url=HttpUrl(keypoint_citation["url"]))
        if "title" in keypoint_citation:
            kp_citation.title = keypoint_citation["title"]
        if "authors" in keypoint_citation:
            kp_citation.authors = keypoint_citation["authors"]
        if "publication_date" in keypoint_citation:
            kp_citation.publication_date = keypoint_citation["publication_date"]
        if "venue" in keypoint_citation:
            kp_citation.venue = keypoint_citation["venue"]
        if "publisher" in keypoint_citation:
            kp_citation.publisher = keypoint_citation["publisher"]

        # Create a mock response with the keypoint citation
        mock_response = ExtractKeyPointsResponse(
            points=[
                KeyPoint(
                    content="Test key point",
                    scope=ScopeEnum.NEWS,
                    citation=kp_citation,
                ),
            ],
        )

        mock_chain.invoke = AsyncMock(return_value=mock_response)

        # Patch the BaseChain constructor to return our mock
        with patch(
            "riskgpt.chains.extract_keypoints.BaseChain", return_value=mock_chain
        ):
            # Create a test request with the request citation
            request = ExtractKeyPointsRequest(
                scope=ScopeEnum.NEWS,
                content="Test content",
                citation=request_citation,
            )

            # Call the function under test
            result = await extract_key_points_chain(request)

            # Verify the result
            assert isinstance(result, ExtractKeyPointsResponse)
            assert len(result.points) == 1

            # Verify the merged citation
            merged_citation = result.points[0].citation
            assert str(merged_citation.url) == expected_merged["url"]
            assert merged_citation.title == expected_merged["title"]
            assert merged_citation.authors == expected_merged["authors"]
            assert str(merged_citation.publication_date) == str(
                expected_merged["publication_date"]
            )
            assert merged_citation.venue == expected_merged["venue"]
            assert merged_citation.publisher == expected_merged["publisher"]

    @pytest.mark.asyncio
    async def test_conflicting_citation_merges(
        self, mock_chain, configure_test_logging
    ):
        """Test merging citations with conflicting data."""
        # Create request citation
        request_citation = Citation(
            url=HttpUrl("https://example.com/request"),
            title="Request Title",
            authors=["Request Author"],
            publication_date=date(2023, 1, 1),
            venue="Request Venue",
            publisher="Request Publisher",
        )

        # Create keypoint citation with conflicting data
        conflicting_citation = Citation(
            url=HttpUrl("https://example.com/conflict"),
            title="Conflict Title",
            authors=["Conflict Author"],
            publication_date=date(2022, 12, 31),
            venue="Conflict Venue",
            publisher="Conflict Publisher",
        )

        # Create a mock response with the conflicting citation
        mock_response = ExtractKeyPointsResponse(
            points=[
                KeyPoint(
                    content="Test key point",
                    scope=ScopeEnum.NEWS,
                    citation=conflicting_citation,
                ),
            ],
        )

        mock_chain.invoke = AsyncMock(return_value=mock_response)

        # Patch the BaseChain constructor to return our mock
        with patch(
            "riskgpt.chains.extract_keypoints.BaseChain", return_value=mock_chain
        ):
            # Create a test request with the request citation
            request = ExtractKeyPointsRequest(
                scope=ScopeEnum.NEWS,
                content="Test content",
                citation=request_citation,
            )

            # Call the function under test
            result = await extract_key_points_chain(request)

            # Verify the result
            assert isinstance(result, ExtractKeyPointsResponse)
            assert len(result.points) == 1

            # Verify that the keypoint citation takes precedence
            merged_citation = result.points[0].citation
            assert str(merged_citation.url) == "https://example.com/conflict"
            assert merged_citation.title == "Conflict Title"
            assert merged_citation.authors == ["Conflict Author"]
            assert str(merged_citation.publication_date) == "2022-12-31"
            assert merged_citation.venue == "Conflict Venue"
            assert merged_citation.publisher == "Conflict Publisher"


# This class is for real integration tests that call the LLM without mocking
class TestIntegrationExtractKeypoints:
    """
    Integration tests for key points extraction with real LLM calls.

    These tests verify that the key points extraction chain works correctly
    with real LLM calls. They are marked as integration tests and will be
    skipped if the OPENAI_API_KEY environment variable is not set.
    """

    # Add real integration tests here when needed
    # These tests should not use mocks and should call the LLM directly
    # They should be marked with @pytest.mark.integration
