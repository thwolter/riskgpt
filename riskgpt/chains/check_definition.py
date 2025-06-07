from langchain_core.output_parsers import PydanticOutputParser

from riskgpt.utils.prompt_loader import load_prompt
from riskgpt.config.settings import RiskGPTSettings
from riskgpt.models.schemas import DefinitionCheckRequest, DefinitionCheckResponse
from riskgpt.registry.chain_registry import register
from .base import BaseChain


@register("check_definition")
def check_definition_chain(request: DefinitionCheckRequest) -> DefinitionCheckResponse:
    settings = RiskGPTSettings()
    prompt_data = load_prompt("check_definition")

    parser = PydanticOutputParser(pydantic_object=DefinitionCheckResponse)
    chain = BaseChain(
        prompt_template=prompt_data["template"],
        parser=parser,
        settings=settings,
        prompt_name="check_definition",
    )

    inputs = request.model_dump()
    inputs["domain_section"] = (
        f"Domain knowledge: {request.domain_knowledge}" if request.domain_knowledge else ""
    )

    return chain.invoke(inputs)


async def async_check_definition_chain(
    request: DefinitionCheckRequest,
) -> DefinitionCheckResponse:
    """Asynchronous wrapper around :func:`check_definition_chain`."""
    settings = RiskGPTSettings()
    prompt_data = load_prompt("check_definition")

    parser = PydanticOutputParser(pydantic_object=DefinitionCheckResponse)
    chain = BaseChain(
        prompt_template=prompt_data["template"],
        parser=parser,
        settings=settings,
        prompt_name="check_definition",
    )

    inputs = request.model_dump()
    inputs["domain_section"] = (
        f"Domain knowledge: {request.domain_knowledge}" if request.domain_knowledge else ""
    )

    return await chain.invoke_async(inputs)
