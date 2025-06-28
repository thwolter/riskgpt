"""Wikipedia search provider implementation."""

from typing import List

from langchain_community.utilities import WikipediaAPIWrapper

from riskgpt.helpers.circuit_breaker import wikipedia_breaker, with_fallback
from riskgpt.helpers.search.base import BaseSearchProvider
from riskgpt.helpers.search.utils import create_fallback_function
from riskgpt.logger import logger
from riskgpt.models.helpers.search import SearchRequest, SearchResponse, SearchResult


class WikipediaSearchProvider(BaseSearchProvider):
    """Wikipedia search provider implementation."""

    def __init__(self):
        """Initialize the Wikipedia search provider."""
        self.fallback = create_fallback_function(self)

    @wikipedia_breaker
    @with_fallback(lambda self, payload: self.fallback(payload))
    async def search(self, payload: SearchRequest) -> SearchResponse:
        """Perform a Wikipedia search and format results."""

        results: List[SearchResult] = []

        try:
            wrapper = WikipediaAPIWrapper(
                wiki_client=None, top_k_results=payload.max_results
            )
            # Note: WikipediaAPIWrapper.load is not async, but we're keeping
            # the method signature async to match the interface
            wiki_results = wrapper.load(payload.query)
            for item in wiki_results:
                results.append(
                    SearchResult(
                        title=item.metadata.get("title", ""),
                        url=item.metadata.get("source", ""),
                        date="",  # Wikipedia doesn't provide date in the same way
                        type=payload.source_type.value,
                        content=item.metadata.get("summary", ""),
                    )
                )
            return SearchResponse(
                results=results, success=bool(results), error_message=""
            )

        except Exception as exc:  # pragma: no cover - search failure should not crash
            logger.error("Wikipedia search failed: %s", exc)
            return self.format_error_response(f"Wikipedia search failed: {exc}")
