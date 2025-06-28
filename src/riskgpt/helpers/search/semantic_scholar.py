"""Semantic Scholar search provider implementation."""

from typing import Dict, List, Union

import requests

from riskgpt.config.settings import RiskGPTSettings
from riskgpt.helpers.circuit_breaker import semantic_scholar_breaker, with_fallback
from riskgpt.helpers.search.base import BaseSearchProvider
from riskgpt.helpers.search.utils import create_fallback_function
from riskgpt.logger import logger
from riskgpt.models.helpers.search import SearchRequest, SearchResponse, SearchResult

settings = RiskGPTSettings()


class SemanticScholarSearchProvider(BaseSearchProvider):
    """Semantic Scholar search provider implementation."""

    def __init__(self):
        """Initialize the Semantic Scholar search provider."""
        self.fallback = create_fallback_function(self)
        self.api_url = "https://api.semanticscholar.org/graph/v1/paper/search"
        self.api_key = (
            settings.SEMANTIC_SCHOLAR_API_KEY.get_secret_value()
            if settings.SEMANTIC_SCHOLAR_API_KEY
            else None
        )

    @semantic_scholar_breaker
    @with_fallback(lambda self, payload: self.fallback(payload))
    def search(self, payload: SearchRequest) -> SearchResponse:
        """Perform a Semantic Scholar search and format results."""

        results: List[SearchResult] = []

        # Prepare headers with API key if available
        headers = {}
        if self.api_key:
            headers["x-api-key"] = self.api_key

        # Prepare query parameters
        params: Dict[str, Union[str, int]] = {
            "query": payload.query,
            "limit": payload.max_results,
            "fields": "title,url,abstract,venue,year,authors",
        }

        try:
            response = requests.get(self.api_url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()

            for paper in data.get("data", []):
                # Extract authors (first 3)
                authors = paper.get("authors", [])
                author_names = [author.get("name", "") for author in authors[:3]]
                author_text = ", ".join(author_names)
                if len(authors) > 3:
                    author_text += " et al."

                # Format content with abstract and metadata
                content = (
                    f"Abstract: {paper.get('abstract', 'No abstract available')}\n"
                )
                content += f"Authors: {author_text}\n"
                content += f"Venue: {paper.get('venue', 'Unknown venue')}\n"
                content += f"Year: {paper.get('year', 'Unknown year')}"

                results.append(
                    SearchResult(
                        title=paper.get("title", ""),
                        url=paper.get("url", ""),
                        date=str(paper.get("year", "")),
                        type=payload.source_type.value,
                        content=content,
                        score=paper.get("score", 0.0),
                    )
                )

            return SearchResponse(
                results=results, success=bool(results), error_message=""
            )

        except Exception as exc:
            logger.error("Semantic Scholar search failed: %s", exc)
            return self.format_error_response(f"Semantic Scholar search failed: {exc}")
