from langchain_core.output_parsers import PydanticOutputParser

from riskgpt.utils.prompt_loader import load_prompt
from riskgpt.config.settings import RiskGPTSettings
import re
from riskgpt.models.schemas import (
    DefinitionCheckRequest,
    DefinitionCheckResponse,
    BiasCheckRequest,
)
from .bias_check import bias_check_chain
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

    response = chain.invoke(inputs)
    bias_res = bias_check_chain(
        BiasCheckRequest(risk_description=response.revised_description, language=request.language)
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
    inputs["domain_section"] = (
        f"Domain knowledge: {request.domain_knowledge}" if request.domain_knowledge else ""
    )

    response = await chain.invoke_async(inputs)
    bias_res = bias_check_chain(
        BiasCheckRequest(risk_description=response.revised_description, language=request.language)
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
