from langchain_core.output_parsers import PydanticOutputParser
from pydantic import HttpUrl

from riskgpt.chains.base import BaseChain
from riskgpt.helpers.prompt_loader import load_prompt
from riskgpt.models.chains.keypoints import (
    ExtractKeyPointsRequest,
    ExtractKeyPointsResponse,
)
from riskgpt.models.helpers.citation import Citation


async def extract_key_points_chain(
    request: ExtractKeyPointsRequest,
) -> ExtractKeyPointsResponse:
    """Extract key points from a source using an LLM."""

    parser = PydanticOutputParser(pydantic_object=ExtractKeyPointsResponse)
    prompt_data = load_prompt("extract_key_points")

    chain = BaseChain(
        prompt_template=prompt_data["template"],
        parser=parser,
        prompt_name=f"extract_{request.scope.value}_key_points",
    )

    inputs = request.model_dump(mode="json", exclude_none=True)
    result = await chain.invoke(inputs)

    # Handle citations for each key point
    for point in result.points:
        # Case 1: If point.citation already includes all available data, keep it as is
        if (
            hasattr(point, "citation")
            and point.citation
            and point.citation.is_complete()
        ):
            continue
        # todo: clen this up, this is a workaround for the fact that the citation model is not fully implemented yet
        # Case 2: If request has a citation with URL, use it
        if request.citation and request.citation.url:
            # If point already has a citation, try to merge with request citation
            if hasattr(point, "citation") and point.citation:
                # Keep existing citation data if it has more information
                request_citation = request.citation.model_copy()
                # Don't override the URL if it already exists
                if not point.citation.url:
                    point.citation.url = request_citation.url
                if not point.citation.title and request_citation.title:
                    point.citation.title = request_citation.title
                if not point.citation.authors and request_citation.authors:
                    point.citation.authors = request_citation.authors
                if (
                    not point.citation.publication_date
                    and request_citation.publication_date
                ):
                    point.citation.publication_date = request_citation.publication_date
                if not point.citation.venue and request_citation.venue:
                    point.citation.venue = request_citation.venue
                if not point.citation.publisher and request_citation.publisher:
                    point.citation.publisher = request_citation.publisher
            else:
                # No existing citation, use the request citation
                point.citation = request.citation
        else:
            # Case 3: Ensure the citation has a URL
            # If we don't have a citation at all, create a minimal one
            if not hasattr(point, "citation") or not point.citation:
                # Create a minimal citation with an empty URL
                # This should not happen in practice since the KeyPoint model requires a citation
                point.citation = Citation(url=HttpUrl("https://example.com"))

    return result
