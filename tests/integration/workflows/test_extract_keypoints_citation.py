from datetime import date
from unittest.mock import AsyncMock, patch

import pytest
from riskgpt.models.chains.keypoints import ExtractKeyPointsResponse, KeyPoint
from riskgpt.models.enums import TopicEnum
from riskgpt.models.helpers.citation import Citation
from riskgpt.models.helpers.search import Source
from riskgpt.workflows.research.nodes import extract_topic_key_points
from riskgpt.workflows.research.state import State


@pytest.mark.asyncio
async def test_extract_topic_key_points_with_citation():
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
        topic=TopicEnum.PEER,
        citation=citation,
    )

    # Create a mock State with the source
    state = State(sources=[source])

    # Create a mock ExtractKeyPointsResponse
    mock_response = ExtractKeyPointsResponse(
        points=[
            KeyPoint(
                content="This is key point 1",
                topic=TopicEnum.PEER,
            ),
            KeyPoint(
                content="This is key point 2",
                topic=TopicEnum.PEER,
            ),
        ],
    )

    # Mock the extract_key_points_chain function
    with patch(
        "riskgpt.workflows.research.nodes.extract_key_points_chain",
        AsyncMock(return_value=mock_response),
    ):
        # Call the extract_topic_key_points function
        result_state = await extract_topic_key_points(state, TopicEnum.PEER)

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
async def test_extract_topic_key_points_without_citation():
    # Create a mock Source without citation
    source = Source(
        title="Example Paper",
        url="https://example.com",
        date="2023",
        type="PEER",
        content="This is an example paper content.",
        topic=TopicEnum.PEER,
    )

    # Create a mock State with the source
    state = State(sources=[source])

    # Create a mock ExtractKeyPointsResponse
    mock_response = ExtractKeyPointsResponse(
        points=[
            KeyPoint(
                content="This is key point 1",
                topic=TopicEnum.PEER,
            ),
            KeyPoint(
                content="This is key point 2",
                topic=TopicEnum.PEER,
            ),
        ],
    )

    # Mock the extract_key_points_chain function
    with patch(
        "riskgpt.workflows.research.nodes.extract_key_points_chain",
        AsyncMock(return_value=mock_response),
    ):
        # Call the extract_topic_key_points function
        result_state = await extract_topic_key_points(state, TopicEnum.PEER)

        # Verify that key points were added to the state
        assert "key_points" in result_state
        assert len(result_state["key_points"]) == 2

        # Verify that each key point has the source URL but no citation
        for key_point in result_state["key_points"]:
            assert key_point.source_url == "https://example.com"
            assert key_point.citation is None

            # Verify that the inline citation falls back to the URL
            assert key_point.get_inline_citation() == "example.com"
