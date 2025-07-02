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
        # Ensure citations is initialized
        if not hasattr(point, "citations"):
            point.citations = []

        # If no citations exist, add the first citation from the request
        if not point.citations and request.citations:
            point.citations = [request.citations[0].model_copy(deep=True)]
            continue

        # Always use the first request citation url for the first point citation
        if point.citations and request.citations:
            point.citations[0].url = request.citations[0].url

            # If the first citation already includes all available data, keep it as is
            if point.citations[0].is_complete():
                continue

            # Otherwise, update the first citation with the request's citation data
            point.citations[0].update_missing_fields(
                source=request.citations[0].model_copy(),
                fields=["title", "authors", "publication_date", "venue", "publisher"],
            )
