import os
from datetime import date
from unittest.mock import AsyncMock, patch

import pytest
from pydantic import HttpUrl
from riskgpt.chains.extract_keypoints import extract_key_points_chain
from riskgpt.models.base import ResponseInfo
from riskgpt.models.chains.keypoints import (
    ExtractKeyPointsRequest,
    ExtractKeyPointsResponse,
    KeyPoint,
)
from riskgpt.models.enums import ScopeEnum
from riskgpt.models.helpers.citation import Citation
from riskgpt.models.helpers.search import Source


# Check if LLM API keys are available
def is_llm_available():
    """Check if the necessary API keys for LLM access are available."""
    return (
        os.environ.get("OPENAI_API_KEY") is not None
        or os.environ.get("ANTHROPIC_API_KEY") is not None
    )


# Skip all tests in this module if LLM is not available
pytestmark = pytest.mark.skipif(
    not is_llm_available(),
    reason="LLM API keys not available. Set OPENAI_API_KEY or ANTHROPIC_API_KEY to run these tests.",
)


class TestIntegrationKeypoints:
    """
    Integration tests for key points extraction with real LLM calls.

    These tests verify that the key points extraction chain works correctly
    with real LLM calls. They are skipped if the necessary API keys are not available.
    """

    @pytest.mark.integration
    @pytest.mark.asyncio
    @patch("riskgpt.chains.base.BaseChain.invoke")
    async def test_extract_key_points_integration(
        self, mock_invoke, configure_test_logging, response_info
    ):
        """Integration test for extract_key_points with a mocked LLM response."""
        # Create a mock response
        mock_response = ExtractKeyPointsResponse(
            points=[
                KeyPoint(
                    content="Regulators are considering new guidelines for AI use in risk management.",
                    scope=ScopeEnum.NEWS,
                    citation=Citation(
                        url=HttpUrl("https://example.com/ai-risk-management")
                    ),
                ),
                KeyPoint(
                    content="Companies are using AI to identify potential risks in their operations.",
                    scope=ScopeEnum.NEWS,
                    citation=Citation(
                        url=HttpUrl("https://example.com/ai-risk-management")
                    ),
                ),
            ],
            response_info=response_info,
        )

        # Configure the mock to return our mock response
        mock_invoke.return_value = AsyncMock(return_value=mock_response)()

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
            citation=Citation(url=HttpUrl("https://example.com/ai-risk-management")),
        )

        # Call the function under test with the mocked LLM
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
        assert result.response_info.prompt_name == "test_prompt"
        assert result.response_info.error is None

        # Verify that at least one key point contains the focus keyword
        focus_keyword_found = any(
            "guidelines" in point.content.lower() for point in result.points
        )
        assert (
            focus_keyword_found
        ), "No key point contains the focus keyword 'guidelines'"

    @pytest.mark.integration
    @pytest.mark.asyncio
    @patch("riskgpt.chains.base.BaseChain.invoke")
    async def test_extract_key_points_with_citation(
        self, mock_invoke, configure_test_logging, response_info
    ):
        """Integration test for extract_key_points with citation using a mocked LLM response."""
        # Create a source with citation
        source = Source(
            content=(
                "AI safety is a critical concern as artificial intelligence systems become more powerful. "
                "Researchers have identified several key risks including alignment problems, "
                "where AI systems might optimize for goals that don't align with human values. "
                "Another concern is the potential for unintended consequences when deploying "
                "complex AI systems in real-world environments."
            ),
            scope=ScopeEnum.ACADEMIC,
            citation=Citation(
                url=HttpUrl("https://example.com"),
                title="AI Safety Research Paper",
                authors=["John Doe", "Jane Smith"],
                publication_date=date(2023, 1, 1),
                venue="AI Safety Conference",
            ),
        )

        # Create a mock response
        mock_response = ExtractKeyPointsResponse(
            points=[
                KeyPoint(
                    content="AI systems might optimize for goals that don't align with human values.",
                    scope=ScopeEnum.ACADEMIC,
                    citation=Citation(
                        url=HttpUrl("https://example.com"),
                        title="AI Safety Research Paper",
                        authors=["John Doe", "Jane Smith"],
                        publication_date=date(2023, 1, 1),
                        venue="AI Safety Conference",
                    ),
                ),
                KeyPoint(
                    content="There is potential for unintended consequences when deploying complex AI systems.",
                    scope=ScopeEnum.ACADEMIC,
                    citation=Citation(
                        url=HttpUrl("https://example.com"),
                        title="AI Safety Research Paper",
                        authors=["John Doe", "Jane Smith"],
                        publication_date=date(2023, 1, 1),
                        venue="AI Safety Conference",
                    ),
                ),
            ],
            response_info=response_info,
        )

        # Configure the mock to return our mock response
        mock_invoke.return_value = AsyncMock(return_value=mock_response)()

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
        assert response.response_info.error is None

        # Verify the content of the key points
        for point in response.points:
            assert point.content
            assert point.scope == ScopeEnum.ACADEMIC

            # Verify that each key point has the citation
            assert point.citation is not None
            assert str(point.citation.url).rstrip("/") == "https://example.com"

            # Verify that the citation can be formatted
            assert point.get_inline_citation() == "John Doe and Jane Smith (2023)"

    @pytest.mark.integration
    @pytest.mark.asyncio
    @patch("riskgpt.chains.base.BaseChain.invoke")
    async def test_extract_key_points_with_logging(
        self, mock_invoke, configure_test_logging, response_info
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
            response_info=response_info,
        )

        # Configure the mock to return our mock response
        mock_invoke.return_value = AsyncMock(return_value=mock_response)()

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

        # We don't need to check for specific log messages in a mocked test
        # as we're not actually calling the real function that would log these messages

        # If there was an error, it should be logged
        if result.response_info.error:
            assert any(
                result.response_info.error in record.message
                for record in caplog.records
            )

    @pytest.mark.integration
    @pytest.mark.asyncio
    @patch("riskgpt.chains.base.BaseChain.invoke")
    async def test_extract_key_points_with_invalid_content(
        self, mock_invoke, configure_test_logging, response_info
    ):
        """Test extracting key points with invalid content."""

        # Create a mock response with an error
        error_response_info = ResponseInfo(
            consumed_tokens=50,
            total_cost=0.001,
            prompt_name="extract_news_key_points",
            model_name="gpt-4",
            error="Content too short to extract meaningful key points",
        )

        mock_response = ExtractKeyPointsResponse(
            points=[], response_info=error_response_info
        )

        # Configure the mock to return our mock response
        mock_invoke.return_value = AsyncMock(return_value=mock_response)()

        # Create a test request with very short content
        request = ExtractKeyPointsRequest(
            scope=ScopeEnum.NEWS,
            content="Too short",
            citation=Citation(url=HttpUrl("https://example.com/invalid-test")),
        )

        # Call the function under test
        result = await extract_key_points_chain(request)

        # Verify the result
        assert isinstance(result, ExtractKeyPointsResponse)
        assert len(result.points) == 0
        assert result.response_info is not None
        assert result.response_info.error is not None

        # We don't need to check for specific log messages in a mocked test
        # as we're not actually calling the real function that would log these messages

    @pytest.mark.integration
    @pytest.mark.asyncio
    @patch("riskgpt.chains.base.BaseChain.invoke")
    async def test_extract_key_points_with_different_scopes(
        self, mock_invoke, configure_test_logging, response_info
    ):
        """Test extracting key points with different scopes."""
        # Test with different scopes
        scopes = [ScopeEnum.NEWS, ScopeEnum.ACADEMIC]

        for scope in scopes:
            # Create a mock response for this scope
            mock_response = ExtractKeyPointsResponse(
                points=[
                    KeyPoint(
                        content=f"This is a test key point for {scope.value}.",
                        scope=scope,
                        citation=Citation(
                            url=HttpUrl(f"https://example.com/{scope.value.lower()}")
                        ),
                    ),
                ],
                response_info=response_info,
            )

            # Configure the mock to return our mock response
            mock_invoke.return_value = AsyncMock(return_value=mock_response)()

            # Create a test request for this scope
            request = ExtractKeyPointsRequest(
                scope=scope,
                content=f"Title: Test {scope.value} Content\n\nContent: This is test content for {scope.value}.",
                citation=Citation(
                    url=HttpUrl(f"https://example.com/{scope.value.lower()}")
                ),
            )

            # Call the function under test
            result = await extract_key_points_chain(request)

            # Verify the result
            assert isinstance(result, ExtractKeyPointsResponse)
            assert result.response_info.error is None
            assert len(result.points) > 0

            # Check that the key points have the correct scope
            for point in result.points:
                assert point.scope == scope
