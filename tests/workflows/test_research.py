import pytest

from riskgpt.models.common import BusinessContext
from riskgpt.models.workflows.context import ResearchRequest, ResearchResponse
from riskgpt.workflows.research import research


@pytest.mark.integration
@pytest.mark.asyncio
class TestSearchProviders:
    @pytest.mark.parametrize("provider", ["tavily", "duckduckgo", "google"])
    async def test_provider(self, monkeypatch, test_request, provider):
        monkeypatch.setattr(
            "riskgpt.config.settings.settings.SEARCH_PROVIDER", provider
        )
        monkeypatch.setattr("riskgpt.config.settings.settings.INCLUDE_WIKIPEDIA", False)
        monkeypatch.setattr(
            "riskgpt.config.settings.settings.SCOPE_SEARCH_PROVIDERS",
            {"news": provider},
        )

        response: ResearchResponse = await research(test_request)
        assert response.summary


@pytest.mark.integration
@pytest.mark.asyncio
class TestWikipediaIntegration:
    async def test_duckduckgo_with_wikipedia(self, monkeypatch, test_request):
        monkeypatch.setattr(
            "riskgpt.config.settings.settings.SEARCH_PROVIDER", "duckduckgo"
        )
        monkeypatch.setattr("riskgpt.config.settings.settings.INCLUDE_WIKIPEDIA", True)
        monkeypatch.setattr(
            "riskgpt.config.settings.settings.SCOPE_SEARCH_PROVIDERS",
            {"news": "duckduckgo"},
        )
        test_request.query = "what is artificial intelligence " + test_request.query

        response: ResearchResponse = await research(test_request)
        assert response.summary


@pytest.mark.integration
@pytest.mark.asyncio
class TestContextAwareWikipedia:
    @pytest.fixture
    def knowledge_request(self):
        return ResearchRequest.from_business_context(
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

    @pytest.fixture
    def news_request(self):
        return ResearchRequest.from_business_context(
            business_context=BusinessContext(
                project_id="AI-Driven Risk Management",
                project_description="A project focused on leveraging AI for risk registration and management.",
                domain_knowledge="artificial intelligence and risk assessment",
            ),
            focus_keywords=[
                "latest AI developments",
                "breaking news in risk management",
            ],
            max_search_results=2,
            region="en-US",
        )

    async def test_context_enabled_knowledge(self, monkeypatch, knowledge_request):
        self._set_context(monkeypatch, True)
        response = await research(knowledge_request)
        assert response.summary

    async def test_context_enabled_news(self, monkeypatch, news_request):
        self._set_context(monkeypatch, True)
        response = await research(news_request)
        assert response.summary

    async def test_context_disabled(self, monkeypatch, news_request):
        self._set_context(monkeypatch, False)
        response = await research(news_request)
        assert response.summary

    def _set_context(self, monkeypatch, context_aware: bool):
        monkeypatch.setattr(
            "riskgpt.config.settings.settings.SEARCH_PROVIDER", "duckduckgo"
        )
        monkeypatch.setattr("riskgpt.config.settings.settings.INCLUDE_WIKIPEDIA", True)
        monkeypatch.setattr(
            "riskgpt.config.settings.settings.WIKIPEDIA_CONTEXT_AWARE", context_aware
        )
