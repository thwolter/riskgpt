from datetime import date
from unittest.mock import AsyncMock, patch

import pytest
from riskgpt.chains.extract_keypoints import extract_key_points_chain
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


@pytest.mark.asyncio
async def test_extract_scope_key_points_with_citation():
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
        topic=ScopeEnum.PEER,  # Required for backward compatibility
        citation=citation,
    )

    # Create a mock State with the source
    state = State(sources=[source])

    # Create a mock ExtractKeyPointsResponse
    mock_response = ExtractKeyPointsResponse(
        points=[
            KeyPoint(
                content="This is key point 1",
                topic=ScopeEnum.PEER,
            ),
            KeyPoint(
                content="This is key point 2",
                topic=ScopeEnum.PEER,
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
    # Create a mock Source without citation
    source = Source(
        title="Example Paper",
        url="https://example.com",
        date="2023",
        type="PEER",
        content="This is an example paper content.",
        scope=ScopeEnum.PEER,
        topic=ScopeEnum.PEER,  # Required for backward compatibility
    )

    # Create a mock State with the source
    state = State(sources=[source])

    # Create a mock ExtractKeyPointsResponse
    mock_response = ExtractKeyPointsResponse(
        points=[
            KeyPoint(
                content="This is key point 1",
                topic=ScopeEnum.PEER,
            ),
            KeyPoint(
                content="This is key point 2",
                topic=ScopeEnum.PEER,
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


@pytest.mark.integration
@pytest.mark.asyncio
async def test_extract_key_points_with_llm():
    """Test extract_key_points_chain with the actual LLM."""
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
        type="PEER",
        content=(
            "AI safety is a critical concern as artificial intelligence systems become more powerful. "
            "Researchers have identified several key risks including alignment problems, "
            "where AI systems might optimize for goals that don't align with human values. "
            "Another concern is the potential for unintended consequences when deploying "
            "complex AI systems in real-world environments."
        ),
        scope=ScopeEnum.PEER,
        topic=ScopeEnum.PEER,  # Required for backward compatibility
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
        assert point.topic == ScopeEnum.PEER

        # Verify that each key point has the source URL and citation
        assert point.source_url == "https://example.com"
        assert point.citation is not None
        assert point.citation == citation

        # Verify that the citation can be formatted
        assert point.get_inline_citation() == "John Doe and Jane Smith (2023)"
