from langchain_core.output_parsers import PydanticOutputParser

from src.models.chains.correlation import (
    CorrelationTagRequest,
    CorrelationTagResponse,
)
from src.registry.chain_registry import register
from src.utils.prompt_loader import load_prompt

from .base import BaseChain


@register("correlation_tags")
async def correlation_tags_chain(
    request: CorrelationTagRequest,
) -> CorrelationTagResponse:
    for risk in request.risks:
        if not risk.id:
            raise ValueError("Each risk must have a unique identifier (id).")

    prompt_data = load_prompt("get_correlation_tags")

    parser = PydanticOutputParser(pydantic_object=CorrelationTagResponse)
    chain = BaseChain(
        prompt_template=prompt_data["template"],
        parser=parser,
        prompt_name="get_correlation_tags",
    )

    inputs = request.model_dump(mode="json", exclude_none=True)
    return await chain.invoke(inputs)
