from unittest.mock import patch

import pytest
from models.base import ResponseInfo
from models.enums import TopicEnum
from models.utils.search import SearchResponse, SearchResult
from models.workflows.context import (
    ExternalContextRequest,
    ExtractKeyPointsResponse,
    KeyPoint,
    KeyPointTextResponse,
)

from src.models.common import BusinessContext
from src.workflows.enrich_context import enrich_context


@pytest.fixture
def test_request():
    """Fixture to create a sample ExternalContextRequest."""
    return ExternalContextRequest(
        business_context=BusinessContext(
            project_id="AI-Driven Risk Management",
            project_description="A project focused on leveraging AI for risk registration and management.",
            domain_knowledge="artificial intelligence and risk assessment",
        ),
        focus_keywords=["AI", "risk management", "data-driven insights"],
    )


@pytest.fixture
def mock_search_result():
    return SearchResponse(
        results=[
            SearchResult(
                title="Two New Chapters in Supply Chain Data-Driven Intelligence - The Maritime Executive",
                url="https://www.maritime-executive.com/editorials/two-new-chapters-in-supply-chain-data-driven-intelligence",
                date="Thu, 19 Jun 2025 03:35:21 GMT",
                type="news",
                content=(
                    "Two New Chapters in Supply Chain Data-Driven Intelligence\n"
                    "Published\nby\nMikael Lind et al.\n\n"
                    "French Shipping Magnate Philippe Louis-Dreyfus Passes at 80\n"
                    "Published\nby\nThe Maritime Executive\n\n"
                    "Former NOAA Officials Call on Industry to Oppose Budget Cuts\n"
                    "Published\nby\nThe Maritime Executive\n\n"
                    "Maritime NZ Charges KiwiRail Over Ro/Ro Grounding\n"
                    "Published\nby\nThe Maritime Executive\n"
                    "Two New Chapters in Supply Chain Data-Driven Intelligence\n\n"
                    "Published\nJun 18, 2025 11:35 PM by\nMikael Lind et al.\n"
                    "[By Mikael Lind, Wolfgang Lehmacher, Xiuju Fu, Jens Lund-Nielsen]\n"
                    "Years of extreme volatility, caused by pandemic shocks, trade wars, and climate-driven disruptions, "
                    "have exposed the complexity of the world’s logistics networks. Thanks to the increasing availability of "
                    "multi-source data and rapid advancements in AI technologies, we now have unprecedented opportunities to "
                    "unravel the complexities of supply chain operations. By harnessing collective intelligence, organizations can "
                    "drive both cost efficiencies and significant reductions in emissions.\n"
                    "The unveiling of project44’s next-generation Movement platform marks another step toward managing supply chain "
                    "and logistics networks more effectively, which are often battered by volatility. With its promise of “Decision Intelligence,” "
                    "a concept not new, Movement is an AI-powered engine designed to transform logistics data into actionable, automated outcomes. "
                    "As the industry assesses this development, a parallel story is unfolding: the rise of the Virtual Watch Tower (VWT), an ecosystem "
                    "comprising supply chain and logistics actors, co-creating a federated, community-driven digital backbone designed to enhance supply "
                    "chain and transport resilience and sustainability, leveraging collective intelligence with multiple source data inputs from different partners.\n"
                    "Both innovations are ambitious, but their philosophies, architectures, and real-world impacts diverge in fundamental ways. This article explores "
                    "these differences, drawing on concrete examples and the lived experience of industry actors, to ask: What kind of digital infrastructure does the "
                    "supply chain truly need?\n"
                    "The Movement Platform’s Vision\n"
                    "Movement by project44 weaves together a network of APIs, connecting over 240,000 carriers, 1,400 telematics partners, and 80+ TMS/ERP systems..."
                    # Note: Truncated for brevity, include full comment as provided in your codebase if needed
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
    monkeypatch.setattr("src.utils.search.settings.SEARCH_PROVIDER", "tavily")
    monkeypatch.setattr("src.utils.search.settings.INCLUDE_WIKIPEDIA", False)
    monkeypatch.setattr("src.utils.search.settings.MAX_SEARCH_RESULTS", 2)
    yield


@pytest.fixture
def mock_search(monkeypatch, mock_search_result):
    """Fixture to patch the search function."""

    def mock_search_func(*args, **kwargs):
        return mock_search_result

    # Patch the search function
    with patch("src.utils.search._tavily_search", side_effect=mock_search_func) as mock:
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
        ).model_dump(),
        points=[
            KeyPoint(
                content="Years of extreme volatility, caused by pandemic shocks, trade wars, and climate-driven disruptions, have exposed the complexity of the world’s logistics networks.",
                topic=TopicEnum.NEWS,
                source_url="https://www.maritime-executive.com/article/two-new-chapters-in-supply-chain-data-driven-intelligence",
            ),
            KeyPoint(
                content="Thanks to the increasing availability of multi-source data and rapid advancements in AI technologies, organizations now have unprecedented opportunities to unravel the complexities of supply chain operations.",
                topic=TopicEnum.NEWS,
                source_url="https://www.maritime-executive.com/article/two-new-chapters-in-supply-chain-data-driven-intelligence",
            ),
            KeyPoint(
                content="Organizations can drive both cost efficiencies and significant reductions in emissions by harnessing collective intelligence.",
                topic=TopicEnum.NEWS,
                source_url="https://www.maritime-executive.com/article/two-new-chapters-in-supply-chain-data-driven-intelligence",
            ),
        ],
    )


@pytest.fixture
def keypoint_text_resp():
    return KeyPointTextResponse(
        model_version="1.0",
        response_info=ResponseInfo(
            consumed_tokens=1068,
            total_cost=0.00018570000000000001,
            prompt_name="keypoint_text",
            model_name="openai:gpt-4.1-nano",
            error=None,
        ).model_dump(),
        text="Years of extreme volatility, driven by pandemic shocks, trade wars, and climate-related disruptions, have exposed the intricate complexity of global logistics networks (maritime-executive.com, 2023). Advances in AI technologies and the growing availability of multi-source data now offer organizations unprecedented opportunities to analyze and manage these complexities effectively (maritime-executive.com, 2023). Furthermore, by harnessing collective intelligence derived from these data sources, organizations can achieve both cost efficiencies and significant reductions in emissions, contributing to more sustainable and resilient supply chain operations (maritime-executive.com, 2023).",
        references=[
            "maritime-executive.com (2023). Two new chapters in supply chain data-driven intelligence. [Online] Available at: https://www.maritime-executive.com/editorials/two-new-chapters-in-supply-chain-data-driven-intelligence [Accessed: 27 April 2024]"
        ],
    )


@pytest.fixture
def mock_extract_key_points(mock_key_points):
    """Fixture to patch extract_key_points function used by enrich_context."""

    # Patch at the location where enrich_context imports/calls it
    with patch(
        "src.workflows.enrich_context.extract_key_points", return_value=mock_key_points
    ) as mock:
        yield mock


@pytest.fixture
def mock_keypoint_text_chain(keypoint_text_resp):
    """Fixture to patch the keypoint text chain."""

    # Patch the keypoint_text_chain to return mock_key_points
    with patch(
        "src.workflows.enrich_context.keypoint_text_chain",
        return_value=keypoint_text_resp,
    ) as mock:
        yield mock


@pytest.mark.integration
@pytest.mark.asyncio
async def test_enrich_context_basic(test_request, mock_settings):
    response = await enrich_context(test_request)
    assert response.sector_summary
    assert isinstance(response.key_points, list)
    assert isinstance(response.sources, list)


@pytest.mark.asyncio
async def test_enrich_context_with_mock(
    test_request,
    mock_settings,
    mock_search,
    mock_extract_key_points,
    mock_keypoint_text_chain,
):
    """Test enrich_context with mocked search results and key points extraction."""

    response = await enrich_context(test_request)

    # Verify the results
    assert len(response.sector_summary) > 0
