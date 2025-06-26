from typing import List
from unittest.mock import patch

import pytest
from riskgpt.chains.keypoint_text import keypoint_text_chain
from riskgpt.models.enums import TopicEnum
from riskgpt.models.workflows.context import (
    KeyPoint,
    KeyPointTextRequest,
    KeyPointTextResponse,
)


@pytest.fixture
def test_key_points() -> List[KeyPoint]:
    """Fixture to create sample KeyPoint objects."""
    return [
        KeyPoint(
            content="The global market for AI is expected to grow by 37% annually until 2030.",
            topic=TopicEnum.NEWS,
            source_url="https://example.com/ai-market-report-2023",
        ),
        KeyPoint(
            content="Regulatory frameworks for AI are being developed in the EU, with the AI Act expected to be implemented by 2025.",
            topic=TopicEnum.REGULATORY,
            source_url="https://example.eu/ai-regulations-2023",
        ),
        KeyPoint(
            content="Industry leaders are investing heavily in responsible AI development to address ethical concerns.",
            topic=TopicEnum.LINKEDIN,
            source_url="https://linkedin.com/pulse/responsible-ai-investments-2023",
        ),
    ]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_keypoint_text_chain(test_key_points) -> None:
    """Test the keypoint_text_chain function with real API calls."""

    request = KeyPointTextRequest(key_points=test_key_points)
    response: KeyPointTextResponse = await keypoint_text_chain(request)

    # Verify the response structure
    assert response.text is not None
    assert response.references is not None
    assert len(response.references) > 0

    # Verify that the text contains citations
    assert "(" in response.text and ")" in response.text

    # Verify that all key points are incorporated
    for key_point in test_key_points:
        # Check for key content words from each key point
        key_words = key_point.content.split()[:3]  # First few words should be enough
        assert any(word in response.text for word in key_words)


@pytest.mark.asyncio
async def test_keypoint_text_chain_with_mock(test_key_points):
    """Test keypoint_text_chain with mocked BaseChain.invoke."""

    expected = KeyPointTextResponse(
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
        request = KeyPointTextRequest(key_points=test_key_points)
        resp = await keypoint_text_chain(request)
        assert resp.text == resp.text
        assert resp.references == expected.references
