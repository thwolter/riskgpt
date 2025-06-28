from unittest.mock import patch

import pytest
from riskgpt.models.base import ResponseInfo
from riskgpt.models.chains.keypoints import (
    ExtractKeyPointsResponse,
    KeyPoint,
    KeyPointSummaryResponse,
)
from riskgpt.models.chains.risk import Risk
from riskgpt.models.common import BusinessContext
from riskgpt.models.enums import TopicEnum
from riskgpt.models.helpers.search import SearchResponse, SearchResult
from riskgpt.models.workflows.risk_analysis import (
    RiskAnalysisRequest,
    RiskAnalysisResponse,
)
from riskgpt.workflows.risk_analysis import analyse_risk


@pytest.fixture
def test_risk():
    """Fixture to create a sample Risk."""
    return Risk(
        title="Data Migration Failure",
        description="Risk of losing critical customer data during migration to the new CRM system",
        category="Technical",
        document_refs=["doc-123", "doc-456"],
    )


@pytest.fixture
def test_request(test_risk):
    """Fixture to create a sample RiskAnalysisRequest."""
    return RiskAnalysisRequest(
        business_context=BusinessContext(
            project_id="CRM-2023",
            project_description="Implementation of a new CRM system",
        ),
        risk=test_risk,
        focus_keywords=["data loss", "migration", "backup"],
        time_horizon_months=6,
        max_search_results=2,
        region="en-US",
    )


@pytest.fixture
def mock_search_result():
    return SearchResponse(
        results=[
            SearchResult(
                title="Best Practices for Data Migration in CRM Systems",
                url="https://example.com/crm-data-migration",
                date="Thu, 19 Jun 2025 03:35:21 GMT",
                type="news",
                content=(
                    "Data migration is a critical process when implementing a new CRM system. "
                    "According to recent studies, 40% of data migrations experience significant issues "
                    "that can lead to data loss or corruption. The main challenges include incompatible "
                    "data formats, incomplete data mapping, and inadequate testing before migration.\n\n"
                    "To mitigate these risks, organizations should follow these best practices:\n"
                    "1. Create a comprehensive data backup before starting the migration\n"
                    "2. Develop a detailed data mapping strategy\n"
                    "3. Implement data validation rules\n"
                    "4. Conduct thorough testing with a subset of data\n"
                    "5. Plan for rollback procedures in case of failure\n\n"
                    "The financial impact of data migration failures can be substantial. A recent report "
                    "by Gartner estimates that large enterprises can lose up to $5 million per hour of "
                    "downtime during a failed migration, not including the potential cost of lost data."
                ),
                score=0.95,
            ),
        ],
        success=True,
        error_message="",
    )


@pytest.fixture
def mock_settings(monkeypatch):
    """Fixture to patch the settings to use tavily as the search provider."""
    monkeypatch.setattr("riskgpt.helpers.search.settings.SEARCH_PROVIDER", "tavily")
    monkeypatch.setattr("riskgpt.helpers.search.settings.INCLUDE_WIKIPEDIA", False)
    yield


@pytest.fixture
def mock_search(monkeypatch, mock_search_result):
    """Fixture to patch the search function."""

    async def mock_search_func(*args, **kwargs):
        return mock_search_result

    # Patch the search function
    with patch("riskgpt.helpers.search.search", side_effect=mock_search_func) as mock:
        yield mock


@pytest.fixture
def mock_key_points():
    return ExtractKeyPointsResponse(
        model_version="1.0",
        response_info=ResponseInfo(
            consumed_tokens=1722,
            total_cost=0.0003228,
            prompt_name="extract_news_key_points",
            model_name="openai:gpt-4.1-nano",
            error=None,
        ),
        points=[
            KeyPoint(
                content="40% of data migrations experience significant issues that can lead to data loss or corruption.",
                topic=TopicEnum.NEWS,
                source_url="https://example.com/crm-data-migration",
            ),
            KeyPoint(
                content="Main challenges in data migration include incompatible data formats, incomplete data mapping, and inadequate testing.",
                topic=TopicEnum.NEWS,
                source_url="https://example.com/crm-data-migration",
            ),
            KeyPoint(
                content="Organizations should create comprehensive data backups before starting migration.",
                topic=TopicEnum.NEWS,
                source_url="https://example.com/crm-data-migration",
            ),
            KeyPoint(
                content="Large enterprises can lose up to $5 million per hour of downtime during a failed migration.",
                topic=TopicEnum.NEWS,
                source_url="https://example.com/crm-data-migration",
            ),
        ],
    )


@pytest.fixture
def keypoint_text_resp():
    return KeyPointSummaryResponse(
        model_version="1.0",
        response_info=ResponseInfo(
            consumed_tokens=1068,
            total_cost=0.00018570000000000001,
            prompt_name="keypoint_text",
            model_name="openai:gpt-4.1-nano",
            error=None,
        ),
        text="Data migration for CRM systems presents significant risks, with 40% of migrations experiencing issues that can lead to data loss or corruption (example.com, 2025). The main challenges include incompatible data formats, incomplete data mapping, and inadequate testing before migration (example.com, 2025). To mitigate these risks, organizations should implement comprehensive data backups before starting the migration process (example.com, 2025). The financial impact can be substantial, with large enterprises potentially losing up to $5 million per hour of downtime during a failed migration (example.com, 2025).",
        references=[
            "example.com (2025). Best Practices for Data Migration in CRM Systems. [Online] Available at: https://example.com/crm-data-migration [Accessed: 19 June 2025]"
        ],
    )


@pytest.fixture
def mock_extract_key_points(mock_key_points):
    """Fixture to patch extract_key_points function used by analyse_risk."""

    async def mock_extract_key_points_func(*args, **kwargs):
        return mock_key_points

    # Patch at the location where analyse_risk imports/calls it
    with patch(
        "riskgpt.chains.extract_keypoints.extract_key_points_chain",
        side_effect=mock_extract_key_points_func,
    ) as mock:
        yield mock


@pytest.fixture
def mock_keypoints_summary_chain(keypoint_text_resp):
    """Fixture to patch the keypoint text chain."""

    async def mock_keypoints_summary_func(*args, **kwargs):
        return keypoint_text_resp

    # Patch the keypoint_text_chain to return mock_key_points
    with patch(
        "riskgpt.chains.keypoints_summary.keypoints_summary_chain",
        side_effect=mock_keypoints_summary_func,
    ) as mock:
        yield mock


@pytest.mark.integration
@pytest.mark.asyncio
async def test_analyse_risk_with_mock(
    test_request,
    mock_settings,
    mock_search,
    mock_extract_key_points,
    mock_keypoints_summary_chain,
) -> None:
    """Test analyse_risk with mocked search results and key points extraction."""

    response: RiskAnalysisResponse = await analyse_risk(test_request)

    # Verify the results
    assert response.risk_summary.startswith("Analyzed risk 'Data Migration Failure'")
    assert len(response.risk_factors) > 0
    assert len(response.mitigation_strategies) > 0
    assert response.impact_assessment
    assert response.document_references == ["doc-123", "doc-456"]
    assert (
        response.full_report
        and "Data migration for CRM systems presents significant risks"
        in response.full_report
    )
    assert (
        response.response_info and response.response_info.prompt_name == "risk_analysis"
    )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_analyse_risk_no_results(
    test_request,
    mock_settings,
    mock_keypoints_summary_chain,
) -> None:
    """Test analyse_risk with no search results."""

    # Create an empty search response
    empty_search_response = SearchResponse(
        results=[],
        success=True,
        error_message="",
    )

    # Mock the search function to return empty results
    async def mock_empty_search(*args, **kwargs):
        return empty_search_response

    with patch("riskgpt.helpers.search.search", side_effect=mock_empty_search):
        response: RiskAnalysisResponse = await analyse_risk(test_request)

        # Verify the results for empty search
        assert response.risk_summary == "No relevant information found for this risk"
        assert len(response.risk_factors) == 0
        assert len(response.mitigation_strategies) == 0
        assert (
            response.impact_assessment
            == "Unable to assess impact due to lack of information"
        )
        assert response.document_references == ["doc-123", "doc-456"]
        assert response.full_report is None


@pytest.mark.integration
@pytest.mark.asyncio
async def test_analyse_risk_search_failure(
    test_request,
    mock_settings,
    mock_keypoints_summary_chain,
) -> None:
    """Test analyse_risk with search failure."""

    # Create a failed search response
    failed_search_response = SearchResponse(
        results=[],
        success=False,
        error_message="Network error",
    )

    # Mock the search function to return failed search
    async def mock_failed_search(*args, **kwargs):
        return failed_search_response

    with patch("riskgpt.helpers.search.search", side_effect=mock_failed_search):
        response: RiskAnalysisResponse = await analyse_risk(test_request)

        # Verify the results for failed search
        assert (
            response.risk_summary
            == "No external data retrieved due to network restrictions or missing dependencies"
        )
        assert len(response.risk_factors) == 0
        assert len(response.mitigation_strategies) == 0
        assert (
            response.impact_assessment
            == "Unable to assess impact due to lack of information"
        )
        assert response.document_references == ["doc-123", "doc-456"]
        assert response.full_report is None
