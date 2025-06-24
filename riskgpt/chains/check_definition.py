from langchain_core.output_parsers import PydanticOutputParser

from riskgpt.models.chains.definition_check import (
    DefinitionCheckRequest,
    DefinitionCheckResponse,
)
from riskgpt.registry.chain_registry import register
from riskgpt.utils.prompt_loader import load_prompt

from .base import BaseChain


@register("check_definition")
async def check_definition_chain(
    request: DefinitionCheckRequest,
) -> DefinitionCheckResponse:
    """Check and improve risk definition."""
    prompt_data = load_prompt("check_definition")

    parser = PydanticOutputParser(pydantic_object=DefinitionCheckResponse)
    chain = BaseChain(
        prompt_template=prompt_data["template"],
        parser=parser,
        prompt_name="check_definition",
    )

    inputs = request.model_dump(mode="json", exclude_none=True)
    return await chain.invoke(inputs)
