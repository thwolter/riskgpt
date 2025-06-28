"""Google search provider implementation."""

from typing import List

from langchain_google_community import GoogleSearchAPIWrapper

from riskgpt.config.settings import RiskGPTSettings
from riskgpt.helpers.circuit_breaker import google_search_breaker, with_fallback
from riskgpt.helpers.search.base import BaseSearchProvider
from riskgpt.logger import logger
from riskgpt.models.helpers.search import SearchRequest, SearchResponse, SearchResult

settings = RiskGPTSettings()


class GoogleSearchProvider(BaseSearchProvider):
    """Google search provider implementation."""

    @google_search_breaker
    @with_fallback(
        lambda self, payload: self.format_error_response(
            "Search service is unavailable"
        )
    )
    def search(self, payload: SearchRequest) -> SearchResponse:
        """Perform a Google Custom Search and format results."""
        results: List[SearchResult] = []
        query = f"{payload.source_type.value} {payload.query}"

        if not settings.GOOGLE_CSE_ID or not settings.GOOGLE_API_KEY:
            logger.warning("Google CSE ID or API key not configured")
            return SearchResponse(
                results=results,
                success=False,
                error_message="Google CSE ID or API key not configured",
            )

        try:
            api_key = settings.GOOGLE_API_KEY.get_secret_value()
            wrapper = GoogleSearchAPIWrapper(
                google_api_key=api_key,
                google_cse_id=settings.GOOGLE_CSE_ID,
                k=payload.max_results,
            )

            search_results = wrapper.results(
                query=query, num_results=payload.max_results
            )

            if not search_results or (
                len(search_results) == 1 and "Result" in search_results[0]
            ):
                logger.warning("No valid search results returned")
                return SearchResponse(
                    results=results,
                    success=False,
                    error_message="No valid search results",
                )

            # Process the results
            for item in search_results:
                results.append(
                    SearchResult(
                        title=item.get("title", ""),
                        url=item.get("link", ""),
                        date="",  # Google doesn't provide date in the same way
                        type=payload.source_type.value,
                        content=item.get("snippet", ""),
                    )
                )

            # Return success only if we have results
            return SearchResponse(
                results=results, success=bool(results), error_message=""
            )

        except Exception as exc:  # pragma: no cover - search failure should not crash
            logger.error("Google search failed: %s", exc)
            return self.format_error_response(f"Google search failed: {exc}")
