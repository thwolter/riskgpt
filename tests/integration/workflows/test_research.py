from unittest.mock import patch

import pytest
from riskgpt.models.base import ResponseInfo
from riskgpt.models.chains.keypoints import (
    ExtractKeyPointsResponse,
    KeyPoint,
    KeyPointSummaryResponse,
)
from riskgpt.models.common import BusinessContext
from riskgpt.models.enums import ScopeEnum
from riskgpt.models.helpers.search import SearchResponse, SearchResult
from riskgpt.models.workflows.context import (
    ResearchRequest,
    ResearchResponse,
)
from riskgpt.workflows.research import research


@pytest.fixture
def test_request():
    """Fixture to create a sample ExternalContextRequest."""
    business_context = BusinessContext(
        project_id="AI-Driven Risk Management",
        project_description="A project focused on leveraging AI for risk registration and management.",
        domain_knowledge="artificial intelligence and risk assessment",
    )
    return ResearchRequest.from_business_context(
        business_context=business_context,
        focus_keywords=["ethic"],
        max_search_results=2,
        region="de-DE",
        # Limit scopes to reduce the research graph
        scopes=[ScopeEnum.NEWS],
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
    # Patch the settings instances in the modules that are used by the research workflow
    monkeypatch.setattr("riskgpt.config.settings.settings.SEARCH_PROVIDER", "tavily")
    monkeypatch.setattr("riskgpt.config.settings.settings.INCLUDE_WIKIPEDIA", False)
    monkeypatch.setattr(
        "riskgpt.helpers.search.__init__.settings.SEARCH_PROVIDER", "tavily"
    )
    monkeypatch.setattr(
        "riskgpt.helpers.search.__init__.settings.INCLUDE_WIKIPEDIA", False
    )
    monkeypatch.setattr(
        "riskgpt.helpers.search.factory.settings.SEARCH_PROVIDER", "tavily"
    )

    # Set up SCOPE_SEARCH_PROVIDERS to use specific providers for each scope
    scope_providers = {
        "news": "tavily",  # Default for tests
        "academic": "semantic_scholar",
        "regulatory": "google",
        "linkedin": "duckduckgo",
        "peer": "tavily",
        "document": "tavily",
    }
    monkeypatch.setattr(
        "riskgpt.config.settings.settings.SCOPE_SEARCH_PROVIDERS", scope_providers
    )
    monkeypatch.setattr(
        "riskgpt.helpers.search.__init__.settings.SCOPE_SEARCH_PROVIDERS",
        scope_providers,
    )

    yield


@pytest.fixture
def mock_search(monkeypatch, mock_search_result):
    """Fixture to patch the search providers instead of the search function.

    This allows the tests to use the specified search provider while still returning mock results.
    """

    # Create a mock search method for any provider
    async def mock_search_method(*args, **kwargs):
        return mock_search_result

    # Patch each provider's search method instead of the entire search function
    with (
        patch(
            "riskgpt.helpers.search.tavily.TavilySearchProvider.search",
            side_effect=mock_search_method,
        ) as tavily_mock,
        patch(
            "riskgpt.helpers.search.duckduckgo.DuckDuckGoSearchProvider.search",
            side_effect=mock_search_method,
        ) as duckduckgo_mock,
        patch(
            "riskgpt.helpers.search.google.GoogleSearchProvider.search",
            side_effect=mock_search_method,
        ) as google_mock,
        patch(
            "riskgpt.helpers.search.wikipedia.WikipediaSearchProvider.search",
            side_effect=mock_search_method,
        ) as wiki_mock,
        patch(
            "riskgpt.helpers.search.semantic_scholar.SemanticScholarSearchProvider.search",
            side_effect=mock_search_method,
        ) as scholar_mock,
    ):
        # Return a dictionary of mocks so tests can verify which provider was used
        yield {
            "tavily": tavily_mock,
            "duckduckgo": duckduckgo_mock,
            "google": google_mock,
            "wikipedia": wiki_mock,
            "semantic_scholar": scholar_mock,
        }


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
                scope=ScopeEnum.NEWS,
                source_url="https://www.maritime-executive.com/article/two-new-chapters-in-supply-chain-data-driven-intelligence",
            ),
            KeyPoint(
                content="Thanks to the increasing availability of multi-source data and rapid advancements in AI technologies, organizations now have unprecedented opportunities to unravel the complexities of supply chain operations.",
                scope=ScopeEnum.NEWS,
                source_url="https://www.maritime-executive.com/article/two-new-chapters-in-supply-chain-data-driven-intelligence",
            ),
            KeyPoint(
                content="Organizations can drive both cost efficiencies and significant reductions in emissions by harnessing collective intelligence.",
                scope=ScopeEnum.NEWS,
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
            prompt_name="keypoint_summary",
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
    """Fixture to patch extract_key_points function used by research."""

    async def mock_extract_key_points_func(*args, **kwargs):
        return mock_key_points

    # Patch at the location where research imports/calls it
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
async def test_research_tavily(
    monkeypatch,
    test_request,
) -> None:
    monkeypatch.setattr("riskgpt.config.settings.settings.SEARCH_PROVIDER", "tavily")
    monkeypatch.setattr("riskgpt.config.settings.settings.INCLUDE_WIKIPEDIA", False)

    scope_providers = {
        "news": "tavily",
    }
    monkeypatch.setattr(
        "riskgpt.config.settings.settings.SCOPE_SEARCH_PROVIDERS", scope_providers
    )

    response: ResearchResponse = await research(test_request)

    assert response.summary


@pytest.mark.integration
@pytest.mark.asyncio
async def test_research_duckduckgo(
    monkeypatch,
    test_request,
) -> None:
    monkeypatch.setattr(
        "riskgpt.config.settings.settings.SEARCH_PROVIDER", "duckduckgo"
    )
    monkeypatch.setattr("riskgpt.config.settings.settings.INCLUDE_WIKIPEDIA", False)

    scope_providers = {
        "news": "duckduckgo",
    }
    monkeypatch.setattr(
        "riskgpt.config.settings.settings.SCOPE_SEARCH_PROVIDERS", scope_providers
    )

    response: ResearchResponse = await research(test_request)

    assert response.summary


@pytest.mark.integration
@pytest.mark.asyncio
async def test_research_google(
    monkeypatch,
    test_request,
) -> None:
    monkeypatch.setattr("riskgpt.config.settings.settings.SEARCH_PROVIDER", "google")
    monkeypatch.setattr("riskgpt.config.settings.settings.INCLUDE_WIKIPEDIA", False)

    scope_providers = {
        "news": "google",
    }
    monkeypatch.setattr(
        "riskgpt.config.settings.settings.SCOPE_SEARCH_PROVIDERS", scope_providers
    )

    response: ResearchResponse = await research(test_request)

    assert response.summary


@pytest.mark.integration
@pytest.mark.asyncio
async def test_research_duckduckgo_and_wikipedia(
    monkeypatch,
    test_request,
) -> None:
    monkeypatch.setattr(
        "riskgpt.config.settings.settings.SEARCH_PROVIDER", "duckduckgo"
    )
    monkeypatch.setattr("riskgpt.config.settings.settings.INCLUDE_WIKIPEDIA", True)

    scope_providers = {
        "news": "duckduckgo",
    }
    monkeypatch.setattr(
        "riskgpt.config.settings.settings.SCOPE_SEARCH_PROVIDERS", scope_providers
    )

    # Make the query look like a knowledge query to trigger Wikipedia inclusion
    test_request.query = "what is artificial intelligence " + test_request.query

    response: ResearchResponse = await research(test_request)

    assert response.summary


@pytest.mark.integration
@pytest.mark.asyncio
async def test_research_with_context_aware_wiki_enabled_knowledge_query(
    monkeypatch,
) -> None:
    """Test research with context-aware wiki enabled and a knowledge query."""
    # Create a request with a knowledge query that should include Wikipedia
    business_context = BusinessContext(
        project_id="AI-Driven Risk Management",
        project_description="A project focused on leveraging AI for risk registration and management.",
        domain_knowledge="artificial intelligence and risk assessment",
    )
    knowledge_request = ResearchRequest.from_business_context(
        business_context=business_context,
        focus_keywords=[
            "what is artificial intelligence",
            "definition of risk management",
        ],
        max_search_results=2,
        region="en-US",
    )

    monkeypatch.setattr(
        "riskgpt.config.settings.settings.SEARCH_PROVIDER", "duckduckgo"
    )
    monkeypatch.setattr("riskgpt.config.settings.settings.INCLUDE_WIKIPEDIA", True)
    monkeypatch.setattr(
        "riskgpt.config.settings.settings.WIKIPEDIA_CONTEXT_AWARE", True
    )

    response: ResearchResponse = await research(knowledge_request)
    assert response.summary


@pytest.mark.integration
@pytest.mark.asyncio
async def test_research_with_context_aware_wiki_enabled_news_query(
    monkeypatch,
) -> None:
    """Test research with context-aware wiki enabled and a news query."""
    # Create a request with a news query that should not include Wikipedia
    business_context = BusinessContext(
        project_id="AI-Driven Risk Management",
        project_description="A project focused on leveraging AI for risk registration and management.",
        domain_knowledge="artificial intelligence and risk assessment",
    )
    news_request = ResearchRequest.from_business_context(
        business_context=business_context,
        focus_keywords=["latest AI developments", "breaking news in risk management"],
        max_search_results=2,
        region="en-US",
    )

    monkeypatch.setattr(
        "riskgpt.config.settings.settings.SEARCH_PROVIDER", "duckduckgo"
    )
    monkeypatch.setattr("riskgpt.config.settings.settings.INCLUDE_WIKIPEDIA", True)
    monkeypatch.setattr(
        "riskgpt.config.settings.settings.WIKIPEDIA_CONTEXT_AWARE", True
    )

    response: ResearchResponse = await research(news_request)
    assert response.summary


@pytest.mark.integration
@pytest.mark.asyncio
async def test_research_with_context_aware_wiki_disabled(
    monkeypatch,
) -> None:
    """Test research with context-aware wiki disabled."""
    # Create a request with a news query, but Wikipedia should be included anyway
    # because context-aware wiki is disabled
    business_context = BusinessContext(
        project_id="AI-Driven Risk Management",
        project_description="A project focused on leveraging AI for risk registration and management.",
        domain_knowledge="artificial intelligence and risk assessment",
    )
    news_request = ResearchRequest.from_business_context(
        business_context=business_context,
        focus_keywords=["latest AI developments", "breaking news in risk management"],
        max_search_results=2,
        region="en-US",
    )

    monkeypatch.setattr(
        "riskgpt.config.settings.settings.SEARCH_PROVIDER", "duckduckgo"
    )
    monkeypatch.setattr("riskgpt.config.settings.settings.INCLUDE_WIKIPEDIA", True)
    monkeypatch.setattr(
        "riskgpt.config.settings.settings.WIKIPEDIA_CONTEXT_AWARE", False
    )

    response: ResearchResponse = await research(news_request)
    assert response.summary
