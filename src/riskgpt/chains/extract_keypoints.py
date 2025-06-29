from langchain_core.output_parsers import PydanticOutputParser

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

    # todo: the attribute additional_citations must be filled in by the chain
    # todo: we have to handel the citation accordingly - when provided, it should be used for all points
    # todo: if not, the citation has to be extracted from the content

    for point in result.points:
        # Use the URL from the citation if available
        if request.citation and request.citation.url:
            point.source_url = request.citation.url
            point.citation = request.citation
        else:
            # Create a minimal citation if none is provided
            url = point.source_url or ""
            point.citation = Citation(url=url)

    return result
