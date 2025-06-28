"""Factory for creating search providers."""

from riskgpt.config.settings import RiskGPTSettings
from riskgpt.helpers.search.base import BaseSearchProvider
from riskgpt.helpers.search.duckduckgo import DuckDuckGoSearchProvider
from riskgpt.helpers.search.google import GoogleSearchProvider
from riskgpt.helpers.search.tavily import TavilySearchProvider
from riskgpt.helpers.search.wikipedia import WikipediaSearchProvider
from riskgpt.logger import logger

settings = RiskGPTSettings()


def get_search_provider() -> BaseSearchProvider:
    """Get the configured search provider."""

    if settings.SEARCH_PROVIDER == "duckduckgo":
        return DuckDuckGoSearchProvider()
    elif settings.SEARCH_PROVIDER == "google":
        return GoogleSearchProvider()
    elif settings.SEARCH_PROVIDER == "wikipedia":
        return WikipediaSearchProvider()
    elif settings.SEARCH_PROVIDER == "tavily":
        return TavilySearchProvider()
    else:
        # Default to DuckDuckGo if provider is not recognized
        logger.warning(
            f"Unknown search provider: {settings.SEARCH_PROVIDER}, defaulting to DuckDuckGo"
        )
        return DuckDuckGoSearchProvider()
