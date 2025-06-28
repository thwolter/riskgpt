"""Semantic Scholar search provider implementation."""

from typing import Dict, List, Union

import aiohttp

from riskgpt.chains import extract_keywords_chain
from riskgpt.config.settings import RiskGPTSettings
from riskgpt.helpers.circuit_breaker import semantic_scholar_breaker, with_fallback
from riskgpt.helpers.search.base import BaseSearchProvider
from riskgpt.helpers.search.utils import create_fallback_function
from riskgpt.logger import logger
from riskgpt.models.chains.keywords import ExtractKeywordsRequest
from riskgpt.models.helpers.search import SearchRequest, SearchResponse, SearchResult

settings = RiskGPTSettings()


class SemanticScholarSearchProvider(BaseSearchProvider):
    """Semantic Scholar search provider implementation."""

    MAX_QUERY_WORDS: int = 5  # Threshold for extracting keywords from long queries

    def __init__(self):
        """Initialize the Semantic Scholar search provider."""
        self.fallback = create_fallback_function(self)
        self.api_url = settings.SEMANTIC_SCHOLAR_URL

        self.api_key = (
            settings.SEMANTIC_SCHOLAR_API_KEY.get_secret_value()
            if settings.SEMANTIC_SCHOLAR_API_KEY
            else None
        )

    @semantic_scholar_breaker
    @with_fallback(lambda self, payload: self.fallback(payload))
    async def search(self, payload: SearchRequest) -> SearchResponse:
        """Perform a Semantic Scholar search and format results."""

        results: List[SearchResult] = []

        headers = {}
        if self.api_key:
            headers["x-api-key"] = self.api_key

        # Extract keywords if the query is longer than a threshold
        query = payload.query
        if len(query.split()) > self.MAX_QUERY_WORDS:
            logger.info(f"Extracted keywords from long query: {query}")
            keywords_response = await extract_keywords_chain(
                ExtractKeywordsRequest(query=query, max_keywords=self.MAX_QUERY_WORDS)
            )
            query = keywords_response.keywords

        # Prepare query parameters
        params: Dict[str, Union[str, int]] = {
            "query": query,
            "limit": payload.max_results,
            "fields": "title,url,abstract,venue,year,authors",
        }

        try:
            async with aiohttp.ClientSession() as session:
                if self.api_key:
                    # Use the API key for authenticated requests
                    headers["x-api-key"] = self.api_key
                    async with session.get(
                        self.api_url, params=params, headers=headers
                    ) as http_response:
                        http_response.raise_for_status()
                        data = await http_response.json()
                else:
                    async with session.get(
                        self.api_url, params=params
                    ) as http_response:
                        http_response.raise_for_status()
                        data = await http_response.json()

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
