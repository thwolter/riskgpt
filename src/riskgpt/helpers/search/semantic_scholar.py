"""Semantic Scholar search provider implementation."""

import asyncio
from typing import Dict, List, Optional, Union

import aiohttp

from riskgpt.chains import extract_keywords_chain
from riskgpt.config.settings import RiskGPTSettings
from riskgpt.helpers.circuit_breaker import semantic_scholar_breaker, with_fallback
from riskgpt.helpers.search.base import BaseSearchProvider
from riskgpt.helpers.search.utils import create_fallback_function
from riskgpt.logger import logger
from riskgpt.models.chains.keywords import ExtractKeywordsRequest
from riskgpt.models.helpers.citation import Citation
from riskgpt.models.helpers.search import SearchRequest, SearchResponse, SearchResult

settings = RiskGPTSettings()


class SemanticScholarSearchProvider(BaseSearchProvider):
    """Semantic Scholar search provider implementation."""

    MAX_QUERY_WORDS: int = 5  # Threshold for extracting keywords from long queries
    MAX_RETRIES: int = 3  # Maximum number of retry attempts for rate-limited requests
    RETRY_BASE_DELAY: float = 1.0  # Base delay in seconds for exponential backoff

    def __init__(self):
        """Initialize the Semantic Scholar search provider."""
        self.fallback = create_fallback_function(self)
        self.api_url = settings.SEMANTIC_SCHOLAR_URL

        self.api_key = (
            settings.SEMANTIC_SCHOLAR_API_KEY.get_secret_value()
            if settings.SEMANTIC_SCHOLAR_API_KEY
            else None
        )

    async def _fetch_with_retry(
        self,
        session: aiohttp.ClientSession,
        url: str,
        params: Dict[str, Union[str, int]],
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict:
        """Fetch data from API with retry logic for rate limiting.

        Args:
            session: The aiohttp ClientSession to use
            url: The URL to fetch data from
            params: Query parameters for the request
            headers: Optional headers for the request

        Returns:
            The JSON response data

        Raises:
            Exception: If all retry attempts fail
        """
        headers = headers or {}
        retry_count = 0

        while True:
            try:
                async with session.get(url, params=params, headers=headers) as response:
                    if response.status == 429:  # Too Many Requests
                        retry_count += 1
                        if retry_count > self.MAX_RETRIES:
                            # If we've exceeded max retries, raise the exception
                            response.raise_for_status()

                        # Calculate backoff delay with exponential increase and some jitter
                        delay = self.RETRY_BASE_DELAY * (2 ** (retry_count - 1))
                        # Add a small random jitter (0-0.5 seconds)
                        delay += asyncio.get_event_loop().time() % 0.5

                        logger.warning(
                            f"Rate limited by Semantic Scholar API. Retrying in {delay:.2f} seconds "
                            f"(attempt {retry_count}/{self.MAX_RETRIES})"
                        )
                        await asyncio.sleep(delay)
                        continue

                    # For any other status code, raise_for_status will handle errors
                    response.raise_for_status()
                    return await response.json()

            except aiohttp.ClientResponseError as e:
                if e.status == 429 and retry_count < self.MAX_RETRIES:
                    # This should be handled by the code above, but just in case
                    continue
                raise

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

                # Use the retry mechanism for API calls
                data = await self._fetch_with_retry(
                    session=session, url=self.api_url, params=params, headers=headers
                )

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

                    # Create Citation object
                    from datetime import datetime

                    publication_date = None
                    if paper.get("year"):
                        try:
                            publication_date = datetime.strptime(
                                str(paper.get("year")), "%Y"
                            ).date()
                        except (ValueError, TypeError):
                            # If year is not a valid format, leave publication_date as None
                            pass

                    citation = Citation(
                        url=paper.get("url", ""),
                        title=paper.get("title", ""),
                        authors=[
                            author.get("name", "")
                            for author in paper.get("authors", [])
                        ],
                        publication_date=publication_date,
                        venue=paper.get("venue"),
                    )

                    results.append(
                        SearchResult(
                            title=paper.get("title", ""),
                            url=paper.get("url", ""),
                            date=str(paper.get("year", "")),
                            type=payload.source_type.value,
                            content=content,
                            score=paper.get("score", 0.0),
                            citation=citation,
                        )
                    )

            return SearchResponse(
                results=results, success=bool(results), error_message=""
            )

        except Exception as exc:
            logger.error("Semantic Scholar search failed: %s", exc)
            return self.format_error_response(f"Semantic Scholar search failed: {exc}")
