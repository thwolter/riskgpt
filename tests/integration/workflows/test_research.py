from unittest.mock import patch

import pytest
from pydantic import HttpUrl
from riskgpt.models.base import ResponseInfo
from riskgpt.models.chains.keypoints import (
    ExtractKeyPointsResponse,
    KeyPoint,
    KeyPointSummaryResponse,
)
from riskgpt.models.common import BusinessContext
from riskgpt.models.enums import ScopeEnum
from riskgpt.models.helpers.citation import Citation
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
                citation=Citation(
                    url=HttpUrl(
                        "https://www.maritime-executive.com/article/two-new-chapters-in-supply-chain-data-driven-intelligence"
                    )
                ),
            ),
            KeyPoint(
                content="Thanks to the increasing availability of multi-source data and rapid advancements in AI technologies, organizations now have unprecedented opportunities to unravel the complexities of supply chain operations.",
                scope=ScopeEnum.NEWS,
                citation=Citation(
                    url=HttpUrl(
                        "https://www.maritime-executive.com/article/two-new-chapters-in-supply-chain-data-driven-intelligence"
                    )
                ),
            ),
            KeyPoint(
                content="Organizations can drive both cost efficiencies and significant reductions in emissions by harnessing collective intelligence.",
                scope=ScopeEnum.NEWS,
                citation=Citation(
                    url=HttpUrl(
                        "https://www.maritime-executive.com/article/two-new-chapters-in-supply-chain-data-driven-intelligence"
                    )
                ),
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
    test_request.scopes = [ScopeEnum.LINKEDIN]

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
