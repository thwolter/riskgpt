from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from riskgpt.models.chains import ExtractKeyPointsResponse
from riskgpt.models.enums import ScopeEnum
from riskgpt.workflows.research.nodes import extract_scope_key_points


class TestExtractionWorkflow:
    """
    Tests for the key points extraction workflow.

    This class tests the extract_scope_key_points function that is used in the
    research workflow to extract key points from sources in a State object.
    """

    @pytest.mark.asyncio
    async def test_extract_scope_key_points_with_citation(
        self, mock_chain, mock_news_keypoints_response, state_with_sources
    ):
        """Test extracting key points with citation information."""
        # Mock the extract_key_points_chain function
        with patch(
            "riskgpt.workflows.research.nodes.extract_key_points_chain",
            AsyncMock(return_value=mock_news_keypoints_response),
        ):
            # Call the extract_scope_key_points function
            result_state = await extract_scope_key_points(
                state_with_sources, ScopeEnum.NEWS
            )

            # Verify that key points were added to the state
            assert "key_points" in result_state
            assert len(result_state["key_points"]) == 2

            # Verify that each key point has the citation
            for key_point in result_state["key_points"]:
                assert key_point.citation is not None
                assert key_point.citation.title == "Example Title"
                assert key_point.citation.authors == ["John Doe"]

                # Verify that the citation can be formatted
                assert key_point.get_inline_citation() == "John Doe (2023)"
                assert result_state.error is None

    @pytest.mark.asyncio
    async def test_extract_scope_key_points_with_empty_sources(self):
        """Test extracting key points with empty sources."""
        # Create a State with no sources
        state = MagicMock()
        state.sources = []

        # Call the extract_scope_key_points function
        result_state = await extract_scope_key_points(state, ScopeEnum.NEWS)

        # Verify that no key points were added to the state
        assert "key_points" not in result_state

        # Verify that an error was set in the state
        assert result_state.error is not None
        assert "No sources found" in result_state.error

    @pytest.mark.asyncio
    async def test_extract_scope_key_points_with_error(
        self, mock_chain, state_with_sources, sample_response_info
    ):
        """Test extracting key points with an error in the chain."""
        # Create a mock response with an error
        error_response = ExtractKeyPointsResponse(
            points=[],
            response_info=sample_response_info(
                "extract_news_key_points", "Error extracting key points"
            ),
        )

        # Mock the extract_key_points_chain function to return an error
        with patch(
            "riskgpt.workflows.research.nodes.extract_key_points_chain",
            AsyncMock(return_value=error_response),
        ):
            # Call the extract_scope_key_points function
            result_state = await extract_scope_key_points(
                state_with_sources, ScopeEnum.NEWS
            )

            # Verify that no key points were added to the state
            assert "key_points" not in result_state

            # Verify that an error was set in the state
            assert result_state.error is not None
            assert "Error extracting key points" in result_state.error
