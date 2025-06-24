from langchain_core.output_parsers import PydanticOutputParser

from riskgpt.models.chains.correlation import (
    CorrelationTagRequest,
    CorrelationTagResponse,
)
from riskgpt.registry.chain_registry import register
from riskgpt.utils.prompt_loader import load_prompt

from .base import BaseChain


@register("get_correlation_tags")
async def get_correlation_tags_chain(
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
