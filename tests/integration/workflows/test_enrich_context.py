from unittest.mock import patch

import pytest
from riskgpt.models.base import ResponseInfo
from riskgpt.models.chains.keypoints import (
    ExtractKeyPointsResponse,
    KeyPoint,
    KeyPointSummaryResponse,
)
from riskgpt.models.common import BusinessContext
from riskgpt.models.enums import TopicEnum
from riskgpt.models.helpers.search import SearchResponse, SearchResult
from riskgpt.models.workflows.context import (
    EnrichContextRequest,
    EnrichContextResponse,
)
from riskgpt.workflows.enrich_context import enrich_context


@pytest.fixture
def test_request():
    """Fixture to create a sample ExternalContextRequest."""
    return EnrichContextRequest(
        business_context=BusinessContext(
            project_id="AI-Driven Risk Management",
            project_description="A project focused on leveraging AI for risk registration and management.",
            domain_knowledge="artificial intelligence and risk assessment",
        ),
        focus_keywords=["ethic"],
        max_search_results=2,
        region="de-DE",
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
    return KeyPointSummaryResponse(
        model_version="1.0",
        response_info=ResponseInfo(
            consumed_tokens=1068,
            total_cost=0.00018570000000000001,
            prompt_name="keypoint_text",
            model_name="openai:gpt-4.1-nano",
            error=None,
        ),
        text="Years of extreme volatility, driven by pandemic shocks, trade wars, and climate-related disruptions, have exposed the intricate complexity of global logistics networks (maritime-executive.com, 2023). Advances in AI technologies and the growing availability of multi-source data now offer organizations unprecedented opportunities to analyze and manage these complexities effectively (maritime-executive.com, 2023). Furthermore, by harnessing collective intelligence derived from these data sources, organizations can achieve both cost efficiencies and significant reductions in emissions, contributing to more sustainable and resilient supply chain operations (maritime-executive.com, 2023).",
        references=[
            "maritime-executive.com (2023). Two new chapters in supply chain data-driven intelligence. [Online] Available at: https://www.maritime-executive.com/editorials/two-new-chapters-in-supply-chain-data-driven-intelligence [Accessed: 27 April 2024]"
        ],
    )


@pytest.fixture
def mock_extract_key_points(mock_key_points):
    """Fixture to patch extract_key_points function used by enrich_context."""

    async def mock_extract_key_points_func(*args, **kwargs):
        return mock_key_points

    # Patch at the location where enrich_context imports/calls it
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
async def test_enrich_context_tavily(
    monkeypatch,
    test_request,
    mock_settings,
    mock_search,
    mock_extract_key_points,
    mock_keypoints_summary_chain,
) -> None:
    monkeypatch.setattr("riskgpt.helpers.search.settings.SEARCH_PROVIDER", "tavily")
    monkeypatch.setattr("riskgpt.helpers.search.settings.INCLUDE_WIKIPEDIA", False)
    response: EnrichContextResponse = await enrich_context(test_request)
    assert response.sector_summary


@pytest.mark.integration
@pytest.mark.asyncio
async def test_enrich_context_duckduckgo(
    monkeypatch,
    test_request,
    mock_settings,
    mock_search,
    mock_extract_key_points,
    mock_keypoints_summary_chain,
) -> None:
    monkeypatch.setattr("riskgpt.helpers.search.settings.SEARCH_PROVIDER", "duckduckgo")
    monkeypatch.setattr("riskgpt.helpers.search.settings.INCLUDE_WIKIPEDIA", False)
    response: EnrichContextResponse = await enrich_context(test_request)
    assert response.sector_summary


@pytest.mark.integration
@pytest.mark.asyncio
async def test_enrich_context_google(
    monkeypatch,
    test_request,
    mock_settings,
    mock_search,
    mock_extract_key_points,
    mock_keypoints_summary_chain,
) -> None:
    monkeypatch.setattr("riskgpt.helpers.search.settings.SEARCH_PROVIDER", "google")
    monkeypatch.setattr("riskgpt.helpers.search.settings.INCLUDE_WIKIPEDIA", False)
    response: EnrichContextResponse = await enrich_context(test_request)
    assert response.sector_summary


@pytest.mark.integration
@pytest.mark.asyncio
async def test_enrich_context_duckduckgo_and_wikipedia(
    monkeypatch,
    test_request,
    mock_settings,
    mock_search,
    mock_extract_key_points,
    mock_keypoints_summary_chain,
) -> None:
    monkeypatch.setattr("riskgpt.helpers.search.settings.SEARCH_PROVIDER", "duckduckgo")
    monkeypatch.setattr("riskgpt.helpers.search.settings.INCLUDE_WIKIPEDIA", True)
    response: EnrichContextResponse = await enrich_context(test_request)
    assert response.sector_summary


@pytest.mark.integration
@pytest.mark.asyncio
async def test_enrich_context_with_context_aware_wiki_enabled_knowledge_query(
    monkeypatch,
    mock_settings,
    mock_search,
    mock_extract_key_points,
    mock_keypoints_summary_chain,
) -> None:
    """Test enrich_context with context-aware wiki enabled and a knowledge query."""
    # Create a request with a knowledge query that should include Wikipedia
    knowledge_request = EnrichContextRequest(
        business_context=BusinessContext(
            project_id="AI-Driven Risk Management",
            project_description="A project focused on leveraging AI for risk registration and management.",
            domain_knowledge="artificial intelligence and risk assessment",
        ),
        focus_keywords=[
            "what is artificial intelligence",
            "definition of risk management",
        ],
        max_search_results=2,
        region="en-US",
    )

    monkeypatch.setattr("riskgpt.helpers.search.settings.SEARCH_PROVIDER", "duckduckgo")
    monkeypatch.setattr("riskgpt.helpers.search.settings.INCLUDE_WIKIPEDIA", True)
    monkeypatch.setattr("riskgpt.helpers.search.settings.WIKIPEDIA_CONTEXT_AWARE", True)

    response: EnrichContextResponse = await enrich_context(knowledge_request)
    assert response.sector_summary


@pytest.mark.integration
@pytest.mark.asyncio
async def test_enrich_context_with_context_aware_wiki_enabled_news_query(
    monkeypatch,
    mock_settings,
    mock_search,
    mock_extract_key_points,
    mock_keypoints_summary_chain,
) -> None:
    """Test enrich_context with context-aware wiki enabled and a news query."""
    # Create a request with a news query that should not include Wikipedia
    news_request = EnrichContextRequest(
        business_context=BusinessContext(
            project_id="AI-Driven Risk Management",
            project_description="A project focused on leveraging AI for risk registration and management.",
            domain_knowledge="artificial intelligence and risk assessment",
        ),
        focus_keywords=["latest AI developments", "breaking news in risk management"],
        max_search_results=2,
        region="en-US",
    )

    monkeypatch.setattr("riskgpt.helpers.search.settings.SEARCH_PROVIDER", "duckduckgo")
    monkeypatch.setattr("riskgpt.helpers.search.settings.INCLUDE_WIKIPEDIA", True)
    monkeypatch.setattr("riskgpt.helpers.search.settings.WIKIPEDIA_CONTEXT_AWARE", True)

    response: EnrichContextResponse = await enrich_context(news_request)
    assert response.sector_summary


@pytest.mark.integration
@pytest.mark.asyncio
async def test_enrich_context_with_context_aware_wiki_disabled(
    monkeypatch,
    mock_settings,
    mock_search,
    mock_extract_key_points,
    mock_keypoints_summary_chain,
) -> None:
    """Test enrich_context with context-aware wiki disabled."""
    # Create a request with a news query, but Wikipedia should be included anyway
    # because context-aware wiki is disabled
    news_request = EnrichContextRequest(
        business_context=BusinessContext(
            project_id="AI-Driven Risk Management",
            project_description="A project focused on leveraging AI for risk registration and management.",
            domain_knowledge="artificial intelligence and risk assessment",
        ),
        focus_keywords=["latest AI developments", "breaking news in risk management"],
        max_search_results=2,
        region="en-US",
    )

    monkeypatch.setattr("riskgpt.helpers.search.settings.SEARCH_PROVIDER", "duckduckgo")
    monkeypatch.setattr("riskgpt.helpers.search.settings.INCLUDE_WIKIPEDIA", True)
    monkeypatch.setattr(
        "riskgpt.helpers.search.settings.WIKIPEDIA_CONTEXT_AWARE", False
    )

    response: EnrichContextResponse = await enrich_context(news_request)
    assert response.sector_summary


# todo: Check this test: It should mock and not call the LLM
@pytest.mark.integration
@pytest.mark.asyncio
async def test_enrich_context_with_mock(
    test_request,
    mock_settings,
    mock_search,
    mock_extract_key_points,
    mock_keypoints_summary_chain,
) -> None:
    """Test enrich_context with mocked search results and key points extraction."""

    response = await enrich_context(test_request)

    # Verify the results
    assert len(response.sector_summary) > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_enrich_context_with_context_aware_wiki_enabled_knowledge_query_mock(
    monkeypatch,
    mock_settings,
    mock_search,
    mock_extract_key_points,
    mock_keypoints_summary_chain,
) -> None:
    """Test enrich_context with context-aware wiki enabled and a knowledge query using mocks."""
    # Create a request with a knowledge query that should include Wikipedia
    knowledge_request = EnrichContextRequest(
        business_context=BusinessContext(
            project_id="AI-Driven Risk Management",
            project_description="A project focused on leveraging AI for risk registration and management.",
            domain_knowledge="artificial intelligence and risk assessment",
        ),
        focus_keywords=[
            "what is artificial intelligence",
            "definition of risk management",
        ],
        max_search_results=2,
        region="en-US",
    )

    monkeypatch.setattr("riskgpt.helpers.search.settings.SEARCH_PROVIDER", "duckduckgo")
    monkeypatch.setattr("riskgpt.helpers.search.settings.INCLUDE_WIKIPEDIA", True)
    monkeypatch.setattr("riskgpt.helpers.search.settings.WIKIPEDIA_CONTEXT_AWARE", True)

    # Mock the _should_include_wikipedia function to verify it's called with the right parameters
    with patch(
        "riskgpt.helpers.search._should_include_wikipedia", return_value=True
    ) as mock_should_include:
        response = await enrich_context(knowledge_request)

        # Verify the results
        assert len(response.sector_summary) > 0
        # Verify that _should_include_wikipedia was called
        mock_should_include.assert_called()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_enrich_context_with_context_aware_wiki_enabled_news_query_mock(
    monkeypatch,
    mock_settings,
    mock_search,
    mock_extract_key_points,
    mock_keypoints_summary_chain,
) -> None:
    """Test enrich_context with context-aware wiki enabled and a news query using mocks."""
    # Create a request with a news query that should not include Wikipedia
    news_request = EnrichContextRequest(
        business_context=BusinessContext(
            project_id="AI-Driven Risk Management",
            project_description="A project focused on leveraging AI for risk registration and management.",
            domain_knowledge="artificial intelligence and risk assessment",
        ),
        focus_keywords=["latest AI developments", "breaking news in risk management"],
        max_search_results=2,
        region="en-US",
    )

    monkeypatch.setattr("riskgpt.helpers.search.settings.SEARCH_PROVIDER", "duckduckgo")
    monkeypatch.setattr("riskgpt.helpers.search.settings.INCLUDE_WIKIPEDIA", True)
    monkeypatch.setattr("riskgpt.helpers.search.settings.WIKIPEDIA_CONTEXT_AWARE", True)

    # Mock the _should_include_wikipedia function to verify it's called with the right parameters
    with patch(
        "riskgpt.helpers.search._should_include_wikipedia", return_value=False
    ) as mock_should_include:
        response = await enrich_context(news_request)

        # Verify the results
        assert len(response.sector_summary) > 0
        # Verify that _should_include_wikipedia was called
        mock_should_include.assert_called()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_enrich_context_with_context_aware_wiki_disabled_mock(
    monkeypatch,
    mock_settings,
    mock_search,
    mock_extract_key_points,
    mock_keypoints_summary_chain,
) -> None:
    """Test enrich_context with context-aware wiki disabled using mocks."""
    # Create a request with a news query, but Wikipedia should be included anyway
    # because context-aware wiki is disabled
    news_request = EnrichContextRequest(
        business_context=BusinessContext(
            project_id="AI-Driven Risk Management",
            project_description="A project focused on leveraging AI for risk registration and management.",
            domain_knowledge="artificial intelligence and risk assessment",
        ),
        focus_keywords=["latest AI developments", "breaking news in risk management"],
        max_search_results=2,
        region="en-US",
    )

    monkeypatch.setattr("riskgpt.helpers.search.settings.SEARCH_PROVIDER", "duckduckgo")
    monkeypatch.setattr("riskgpt.helpers.search.settings.INCLUDE_WIKIPEDIA", True)
    monkeypatch.setattr(
        "riskgpt.helpers.search.settings.WIKIPEDIA_CONTEXT_AWARE", False
    )

    # Mock the _should_include_wikipedia function to verify it's NOT called when context-aware is disabled
    with patch(
        "riskgpt.helpers.search._should_include_wikipedia"
    ) as mock_should_include:
        response = await enrich_context(news_request)

        # Verify the results
        assert len(response.sector_summary) > 0
        # Verify that _should_include_wikipedia was NOT called when context-aware is disabled
        mock_should_include.assert_not_called()
