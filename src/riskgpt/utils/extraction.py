from langchain_core.output_parsers import PydanticOutputParser

from src.riskgpt.chains.base import BaseChain
from src.riskgpt.models.workflows.context import (
    ExtractKeyPointsRequest,
    ExtractKeyPointsResponse,
)
from src.riskgpt.utils.prompt_loader import load_prompt


async def extract_key_points(
    request: ExtractKeyPointsRequest,
) -> ExtractKeyPointsResponse:
    """Extract key points from a source using an LLM."""

    parser = PydanticOutputParser(pydantic_object=ExtractKeyPointsResponse)
    prompt_data = load_prompt("extract_key_points")

    chain = BaseChain(
        prompt_template=prompt_data["template"],
        parser=parser,
        prompt_name=f"extract_{request.source_type}_key_points",
    )

    inputs = request.model_dump(mode="json", exclude_none=True)
    result = await chain.invoke(inputs)
    return result
