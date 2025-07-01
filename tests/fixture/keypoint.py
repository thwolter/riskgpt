import pytest

from riskgpt.models.base import ResponseInfo
from riskgpt.models.chains.keypoints import (
    ExtractKeyPointsResponse,
    KeyPoint,
)
from riskgpt.models.enums import ScopeEnum


@pytest.fixture
def news_keypoint(complete_citation):
    """Return a news keypoint with complete citation."""
    return KeyPoint(
        content="Key point about technology",
        scope=ScopeEnum.NEWS,
        citation=complete_citation,
    )


@pytest.fixture
def academic_keypoint(complete_citation):
    """Return an academic keypoint with complete citation."""
    return KeyPoint(
        content="Academic finding",
        scope=ScopeEnum.ACADEMIC,
        citation=complete_citation,
    )


@pytest.fixture
def mock_keypoints_response(news_keypoint, academic_keypoint, sample_response_info):
    """Return a mock ExtractKeyPointsResponse with mixed keypoints."""
    return ExtractKeyPointsResponse(
        points=[news_keypoint, academic_keypoint], response_info=sample_response_info
    )


@pytest.fixture
def mock_news_keypoints_response(complete_citation):
    """Return a mock ExtractKeyPointsResponse with news keypoints."""
    return ExtractKeyPointsResponse(
        points=[
            KeyPoint(
                content="Key point 1 about technology",
                scope=ScopeEnum.NEWS,
                citation=complete_citation,
            ),
            KeyPoint(
                content="Key point 2 about finance",
                scope=ScopeEnum.NEWS,
                citation=complete_citation,
            ),
        ],
        response_info=ResponseInfo(
            consumed_tokens=100,
            total_cost=0.002,
            prompt_name="extract_news_key_points",
            model_name="gpt-4",
        ),
    )


@pytest.fixture
def mock_academic_keypoints_response(complete_citation):
    """Return a mock ExtractKeyPointsResponse with academic keypoints."""
    return ExtractKeyPointsResponse(
        points=[
            KeyPoint(
                content="Research finding 1",
                scope=ScopeEnum.PEER,
                citation=complete_citation,
            ),
            KeyPoint(
                content="Research finding 2",
                scope=ScopeEnum.PEER,
                citation=complete_citation,
            ),
        ],
        response_info=ResponseInfo(
            consumed_tokens=120,
            total_cost=0.0024,
            prompt_name="extract_research_key_points",
            model_name="gpt-4",
        ),
    )
