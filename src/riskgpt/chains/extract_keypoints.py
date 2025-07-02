from langchain_core.output_parsers import PydanticOutputParser

from riskgpt.chains.base import BaseChain
from riskgpt.helpers.prompt_loader import load_prompt
from riskgpt.models.chains.keypoints import (
    ExtractKeyPointsRequest,
    ExtractKeyPointsResponse,
)


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

    await handle_citations(result, request)

    return result


async def handle_citations(result, request):
    # Handle citations for each key point
    for point in result.points:
        # Always use the request's citation url
        point.citation.url = request.citation.url

        # If point.citation already includes all available data, keep it as is
        if point.citation.is_complete():
            continue

        # Otherwise, update the point's citation with the request's citation data
        point.citation.update_missing_fields(
            source=request.citation.model_copy(),
            fields=["title", "authors", "publication_date", "venue", "publisher"],
        )
