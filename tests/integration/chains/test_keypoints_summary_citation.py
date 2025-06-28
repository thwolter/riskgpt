from datetime import date
from unittest.mock import AsyncMock, patch

import pytest
from riskgpt.chains.keypoints_summary import keypoints_summary_chain
from riskgpt.models.chains.keypoints import (
    KeyPoint,
    KeyPointSummaryRequest,
    KeyPointSummaryResponse,
)
from riskgpt.models.enums import TopicEnum
from riskgpt.models.helpers.citation import Citation


@pytest.mark.asyncio
async def test_keypoints_summary_with_citations():
    # Create Citations
    citation1 = Citation(
        url="https://example.com/paper1",
        title="Example Paper 1",
        authors=["John Doe", "Jane Smith"],
        publication_date=date(2023, 1, 1),
        venue="Example Conference",
    )

    citation2 = Citation(
        url="https://example.com/paper2",
        title="Example Paper 2",
        authors=["Alice Johnson"],
        publication_date=date(2022, 5, 15),
        venue="Another Journal",
    )

    # Create KeyPoints with citations
    key_points = [
        KeyPoint(
            content="This is key point 1",
            topic=TopicEnum.PEER,
            source_url="https://example.com/paper1",
            citation=citation1,
        ),
        KeyPoint(
            content="This is key point 2",
            topic=TopicEnum.PEER,
            source_url="https://example.com/paper2",
            citation=citation2,
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
        "riskgpt.chains.base.BaseChain.invoke", AsyncMock(return_value=mock_response)
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
            "John Doe and Jane Smith (2023). Example Paper 1." in response.references[0]
        )
        assert "Alice Johnson (2022). Example Paper 2." in response.references[1]


@pytest.mark.asyncio
async def test_keypoints_summary_with_mixed_citations():
    # Create a Citation
    citation = Citation(
        url="https://example.com/paper",
        title="Example Paper",
        authors=["John Doe"],
        publication_date=date(2023, 1, 1),
        venue="Example Conference",
    )

    # Create KeyPoints with mixed citation sources
    key_points = [
        KeyPoint(
            content="This is key point 1",
            topic=TopicEnum.PEER,
            source_url="https://example.com/paper",
            citation=citation,
        ),
        KeyPoint(
            content="This is key point 2",
            topic=TopicEnum.NEWS,
            source_url="https://news.example.com/article",
            # No citation for this one
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
        "riskgpt.chains.base.BaseChain.invoke", AsyncMock(return_value=mock_response)
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
