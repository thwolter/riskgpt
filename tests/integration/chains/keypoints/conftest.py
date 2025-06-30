import logging
from datetime import date
from unittest.mock import AsyncMock

import pytest
from pydantic import HttpUrl
from riskgpt.logger import configure_logging
from riskgpt.models.base import ResponseInfo
from riskgpt.models.chains.keypoints import (
    ExtractKeyPointsResponse,
    KeyPoint,
)
from riskgpt.models.enums import ScopeEnum
from riskgpt.models.helpers.citation import Citation
from riskgpt.models.helpers.search import Source
from riskgpt.workflows.research.state import State


@pytest.fixture
def configure_test_logging(caplog):
    """Configure logging for tests."""
    caplog.set_level(logging.INFO, logger="riskgpt")
    configure_logging(level=logging.INFO)
    return caplog


@pytest.fixture
def response_info():
    """Return a ResponseInfo object with mock data."""
    return ResponseInfo(
        consumed_tokens=100,
        total_cost=0.002,
        prompt_name="test_prompt",
        model_name="gpt-4",
    )


@pytest.fixture
def complete_citation():
    """Return a complete citation with all fields populated."""
    return Citation(
        url=HttpUrl("https://example.com"),
        title="Example Title",
        authors=["John Doe"],
        publication_date=date(2023, 1, 1),
        venue="Example Venue",
        publisher="Example Publisher",
    )


@pytest.fixture
def minimal_citation():
    """Return a minimal citation with only URL."""
    return Citation(url=HttpUrl("https://example.com"))


@pytest.fixture
def partial_citation():
    """Return a partial citation with URL and title."""
    return Citation(
        url=HttpUrl("https://example.com"),
        title="Example Title",
    )


@pytest.fixture
def news_source(complete_citation):
    """Return a news source with complete citation."""
    return Source(
        content="This is a test news article about technology and finance.",
        scope=ScopeEnum.NEWS,
        citation=complete_citation,
    )


@pytest.fixture
def academic_source(complete_citation):
    """Return an academic source with complete citation."""
    return Source(
        content="This is a test academic paper with important findings.",
        scope=ScopeEnum.ACADEMIC,
        citation=complete_citation,
    )


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
def mock_keypoints_response(news_keypoint, academic_keypoint):
    """Return a mock ExtractKeyPointsResponse with mixed keypoints."""
    return ExtractKeyPointsResponse(
        points=[news_keypoint, academic_keypoint],
        response_info=ResponseInfo(
            consumed_tokens=100,
            total_cost=0.002,
            prompt_name="extract_key_points",
            model_name="gpt-4",
        ),
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


@pytest.fixture
def mock_chain():
    """Return a mock chain that can be configured with different responses."""
    mock = AsyncMock()
    mock.invoke = AsyncMock()
    return mock


@pytest.fixture
def state_with_sources(news_source, academic_source):
    """Return a State object with news and academic sources."""
    return State(sources=[news_source, academic_source])
