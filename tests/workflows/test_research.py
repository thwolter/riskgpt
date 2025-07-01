import pytest

from riskgpt.models.common import BusinessContext
from riskgpt.models.enums import ScopeEnum
from riskgpt.models.workflows.context import (
    ResearchRequest,
    ResearchResponse,
)
from riskgpt.workflows.research import research


# Tests for different search providers
# These tests verify that the research workflow works with different search providers
@pytest.mark.integration
@pytest.mark.asyncio
async def test_research_tavily(
    monkeypatch,
    test_request,
) -> None:
    """Test research workflow using Tavily as the search provider."""
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
    """Test research workflow using DuckDuckGo as the search provider."""
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
    """Test research workflow using Google as the search provider with LinkedIn scope."""
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


# Test for Wikipedia integration
# This test verifies that Wikipedia results can be included in the research
@pytest.mark.integration
@pytest.mark.asyncio
async def test_research_duckduckgo_and_wikipedia(
    monkeypatch,
    test_request,
) -> None:
    """Test research workflow using DuckDuckGo with Wikipedia integration for knowledge queries."""
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


# Tests for context-aware Wikipedia functionality
# These tests verify that Wikipedia results are included or excluded based on context awareness settings
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
