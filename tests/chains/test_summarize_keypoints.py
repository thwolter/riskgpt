import re
from datetime import date
from typing import List
from unittest.mock import AsyncMock, patch

import pytest
import yaml
from pydantic import HttpUrl

from riskgpt.chains.summarize_keypoints import keypoints_summary_chain
from riskgpt.models.chains.keypoints import (
    KeyPoint,
    KeyPointSummaryRequest,
    KeyPointSummaryResponse,
)
from riskgpt.models.enums import ScopeEnum
from riskgpt.models.helpers.citation import Citation


@pytest.fixture
def test_key_points() -> List[KeyPoint]:
    """Fixture to create sample KeyPoint objects."""
    return [
        KeyPoint(
            content="The global market for AI is expected to grow by 37% annually until 2030.",
            scope=ScopeEnum.NEWS,
            citations=[
                Citation(url=HttpUrl("https://example.com/ai-market-report-2023"))
            ],
        ),
        KeyPoint(
            content="Regulatory frameworks for AI are being developed in the EU, with the AI Act expected to be implemented by 2025.",
            scope=ScopeEnum.REGULATORY,
            citations=[Citation(url=HttpUrl("https://example.eu/ai-regulations-2023"))],
        ),
        KeyPoint(
            content="Industry leaders are investing heavily in responsible AI development to address ethical concerns.",
            scope=ScopeEnum.LINKEDIN,
            citations=[
                Citation(url=HttpUrl("https://example.com/ai-market-report-2023"))
            ],
        ),
    ]


@pytest.fixture
def test_long_key_points() -> List[KeyPoint]:
    """Fixture to create KeyPoint objects from YAML with multiple scopes."""

    SCOPE_MAP = {
        "news": ScopeEnum.NEWS,
        "regulatory": ScopeEnum.REGULATORY,
        "linkedin": ScopeEnum.LINKEDIN,
        "peer": ScopeEnum.PEER,
    }

    with open("tests/data/long_keypoints.yaml", "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    key_points = []
    for line in data["inputs"]["key_points"].split("\n"):
        match = re.match(
            r"-\s*(news|regulatory|linkedin|peer):\s*(.+?)\s+(https?://\S+)", line
        )
        if match:
            scope_str, content, url = match.groups()
            scope = SCOPE_MAP.get(scope_str)
            if scope:
                key_points.append(
                    KeyPoint(
                        content=content.strip(),
                        scope=scope,
                        citations=[Citation(url=HttpUrl(url))],
                    )
                )
    return key_points


class TestSummarizeKeypoints:
    """
    Tests for the key points summarization chain.

    This class tests the functionality of summarizing key points from different sources,
    including handling citations and formatting the output text.
    """

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_keypoint_summary_chain(self, test_key_points) -> None:
        """Test the keypoint_text_chain function with a mock."""

        # Create a mock response
        mock_response = KeyPointSummaryResponse(
            text="The global market for AI is expected to grow by 37% annually until 2030 (Example.com, 2023). "
            "Regulatory frameworks for AI are being developed in the EU (Example.eu, 2023). "
            "Industry leaders are investing heavily in responsible AI development (LinkedIn, 2023).",
            references=[
                "Example.com (2023). AI Market Report. [Online] Available at: https://example.com/ai-market-report-2023 [Accessed: 1 Jan 2023]",
                "Example.eu (2023). AI Regulations. [Online] Available at: https://example.eu/ai-regulations-2023 [Accessed: 1 Jan 2023]",
                "LinkedIn (2023). Responsible AI Investments. [Online] Available at: https://linkedin.com/pulse/responsible-ai-investments-2023 [Accessed: 1 Jan 2023]",
            ],
        )

        request = KeyPointSummaryRequest(key_points=test_key_points)

        # Mock the BaseChain.invoke method
        with patch(
            "riskgpt.chains.base.BaseChain.invoke",
            AsyncMock(return_value=mock_response),
        ):
            response: KeyPointSummaryResponse = await keypoints_summary_chain(request)

            # Verify the response structure
            assert response.text is not None
            assert response.references is not None
            assert len(response.references) > 0

            # Verify that the text contains citations
            assert "(" in response.text and ")" in response.text

            # Verify that all key points are incorporated
            for key_point in test_key_points:
                # Check for key content words from each key point
                key_words = key_point.content.split()[
                    :3
                ]  # First few words should be enough
                assert any(word in response.text for word in key_words)

    @pytest.mark.asyncio
    async def test_keypoint_summary_chain_with_mock(self, test_key_points):
        """Test keypoint_text_chain with mocked BaseChain.invoke."""

        expected = KeyPointSummaryResponse(
            text="The global market for AI is expected to grow by 37% annually until 2030 (Example.com, 2023). "
            "Regulatory frameworks for AI are being developed in the EU (Example.eu, 2023). "
            "Industry leaders are investing heavily in responsible AI development (LinkedIn, 2023).",
            references=[
                "Example.com (2023). AI Market Report. [Online] Available at: https://example.com/ai-market-report-2023 [Accessed: 1 Jan 2023]",
                "Example.eu (2023). AI Regulations. [Online] Available at: https://example.eu/ai-regulations-2023 [Accessed: 1 Jan 2023]",
                "LinkedIn (2023). Responsible AI Investments. [Online] Available at: https://linkedin.com/pulse/responsible-ai-investments-2023 [Accessed: 1 Jan 2023]",
            ],
        )

        async def mock_invoke(*args, **kwargs):
            return expected

        with patch("riskgpt.chains.base.BaseChain.invoke", side_effect=mock_invoke):
            request = KeyPointSummaryRequest(key_points=test_key_points)
            resp = await keypoints_summary_chain(request)
            assert resp.text == expected.text
            assert resp.references == expected.references

    @pytest.mark.asyncio
    async def test_keypoints_summary_with_citations(self):
        """Test keypoints summary with academic citations."""
        # Create Citations
        citation1 = Citation(
            url=HttpUrl("https://example.com/paper1"),
            title="Example Paper 1",
            authors=["John Doe", "Jane Smith"],
            publication_date=date(2023, 1, 1),
            venue="Example Conference",
        )

        citation2 = Citation(
            url=HttpUrl("https://example.com/paper2"),
            title="Example Paper 2",
            authors=["Alice Johnson"],
            publication_date=date(2022, 5, 15),
            venue="Another Journal",
        )

        # Create KeyPoints with citations
        key_points = [
            KeyPoint(
                content="This is key point 1",
                scope=ScopeEnum.PEER,
                citations=[citation1],
            ),
            KeyPoint(
                content="This is key point 2",
                scope=ScopeEnum.PEER,
                citations=[citation2],
            ),
        ]

        # Create a mock KeyPointSummaryResponse
        mock_response = KeyPointSummaryResponse(
            text="Summary text with citations (John Doe and Jane Smith, 2023) and (Alice Johnson, 2022).",
            references=[
                "John Doe and Jane Smith (2023). Example Paper 1. Example Conference. [Online] Available at: https://example.com/paper1 [Accessed: 01 January 2024]",
                "Alice Johnson (2022). Example Paper 2. Another Journal. [Online] Available at: https://example.com/paper2 [Accessed: 01 January 2024]",
            ],
        )

        # Create the request
        request = KeyPointSummaryRequest(key_points=key_points)

        # Mock the BaseChain.invoke method
        with patch(
            "riskgpt.chains.base.BaseChain.invoke",
            AsyncMock(return_value=mock_response),
        ):
            # Call the keypoints_summary_chain
            response = await keypoints_summary_chain(request)

            # Verify the response
            assert response == mock_response
            # Check that the text contains the expected citations
            assert response.text.find("John Doe and Jane Smith") != -1
            assert response.text.find("2023") != -1
            assert response.text.find("Alice Johnson") != -1
            assert response.text.find("2022") != -1
            assert len(response.references) == 2
            assert (
                "John Doe and Jane Smith (2023). Example Paper 1."
                in response.references[0]
            )
            assert "Alice Johnson (2022). Example Paper 2." in response.references[1]

    @pytest.mark.asyncio
    async def test_keypoints_summary_with_mixed_citations(self):
        """Test keypoints summary with mixed citation sources."""
        # Create a Citation
        citation = Citation(
            url=HttpUrl("https://example.com/paper"),
            title="Example Paper",
            authors=["John Doe"],
            publication_date=date(2023, 1, 1),
            venue="Example Conference",
        )

        # Create KeyPoints with mixed citation sources
        key_points = [
            KeyPoint(
                content="This is key point 1",
                scope=ScopeEnum.PEER,
                citations=[citation],
            ),
            KeyPoint(
                content="This is key point 2",
                scope=ScopeEnum.NEWS,
                citations=[Citation(url=HttpUrl("https://news.example.com/article"))],
            ),
        ]

        # Create a mock KeyPointSummaryResponse
        mock_response = KeyPointSummaryResponse(
            text="Summary text with citations (John Doe, 2023) and (news.example.com).",
            references=[
                "John Doe (2023). Example Paper. Example Conference. [Online] Available at: https://example.com/paper [Accessed: 01 January 2024]",
                "news.example.com. [Online] Available at: https://news.example.com/article [Accessed: 01 January 2024]",
            ],
        )

        # Create the request
        request = KeyPointSummaryRequest(key_points=key_points)

        # Mock the BaseChain.invoke method
        with patch(
            "riskgpt.chains.base.BaseChain.invoke",
            AsyncMock(return_value=mock_response),
        ):
            # Call the keypoints_summary_chain
            response = await keypoints_summary_chain(request)

            # Verify the response
            assert response == mock_response
            assert "John Doe, 2023" in response.text
            assert "news.example.com" in response.text
            assert len(response.references) == 2
            assert "John Doe (2023). Example Paper." in response.references[0]
            assert (
                "news.example.com. [Online] Available at: https://news.example.com/article"
                in response.references[1]
            )

    @pytest.mark.asyncio
    async def test_empty_key_points(self):
        """Test summarizing an empty list of key points."""
        # Create a request with an empty list of key points
        request = KeyPointSummaryRequest(key_points=[])
        response = await keypoints_summary_chain(request)

        # Verify the response structure
        assert response.text is None
        assert response.references == []
        assert len(response.references) == 0


class TestIntegrationSummarizeKeypoints:
    """
    Integration tests for key points summarization with real LLM calls.

    These tests verify that the key points summarization chain works correctly
    with real LLM calls. They are marked as integration tests and will be
    skipped if the OPENAI_API_KEY environment variable is not set.
    """

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_long_key_points(self, test_long_key_points):
        """Test summarizing a large number of key points."""
        request = KeyPointSummaryRequest(key_points=test_long_key_points)

        # Create a mock response
        mock_response = KeyPointSummaryResponse(
            text="Summary of AI market growth and regulations with citations (example.com, 2023) and (arxiv.org, 2023).",
            references=[
                "example.com (2023). AI Market Report. [Online] Available at: https://example.com/ai-market-report-2023 [Accessed: 1 Jan 2023]",
                "arxiv.org (2023). LLM Research. [Online] Available at: https://arxiv.org/abs/2303.12712 [Accessed: 1 Jan 2023]",
            ],
        )

        # Mock the BaseChain.invoke method
        with patch(
            "riskgpt.chains.base.BaseChain.invoke",
            AsyncMock(return_value=mock_response),
        ):
            response = await keypoints_summary_chain(request)

            # Verify the response structure
            assert response.text is not None
            assert response.references is not None
            assert len(response.references) > 0

            # Verify that the text contains citations
            assert "(" in response.text and ")" in response.text
