import re

from langchain_core.output_parsers import PydanticOutputParser

from riskgpt.config.settings import RiskGPTSettings
from riskgpt.models.schemas import (
    BiasCheckRequest,
    DefinitionCheckRequest,
    DefinitionCheckResponse,
)
from riskgpt.registry.chain_registry import register
from riskgpt.utils.prompt_loader import load_prompt

from .base import BaseChain
from .bias_check import bias_check_chain


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
    inputs["domain_section"] = request.business_context.get_domain_section()

    response = chain.invoke(inputs)
    bias_res = bias_check_chain(
        BiasCheckRequest(
            risk_description=response.revised_description,
            language=request.business_context.language,
        )
    )

    extras = []
    desc = response.revised_description.lower()
    if re.search(r"\bmay\b|\bcould\b|\bpossibly\b", desc):
        extras.append("ambiguous wording")
    if re.search(r"\b(is|was|were|be|been|being|are)\b\s+\w+ed\b", desc):
        extras.append("passive voice")
    if not re.search(r"\d", desc):
        extras.append("missing quantifiers")

    response.biases = list(set((bias_res.biases or []) + extras))
    return response


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
    inputs["domain_section"] = request.business_context.get_domain_section()

    response = await chain.invoke_async(inputs)
    bias_res = bias_check_chain(
        BiasCheckRequest(
            risk_description=response.revised_description,
            language=request.business_context.language,
        )
    )

    extras = []
    desc = response.revised_description.lower()
    if re.search(r"\bmay\b|\bcould\b|\bpossibly\b", desc):
        extras.append("ambiguous wording")
    if re.search(r"\b(is|was|were|be|been|being|are)\b\s+\w+ed\b", desc):
        extras.append("passive voice")
    if not re.search(r"\d", desc):
        extras.append("missing quantifiers")

    response.biases = list(set((bias_res.biases or []) + extras))
    return response
