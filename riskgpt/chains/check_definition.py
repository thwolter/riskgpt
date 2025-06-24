import re
from typing import List

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


async def _process_response(
    response: DefinitionCheckResponse, request: DefinitionCheckRequest
) -> DefinitionCheckResponse:
    """Helper function to process the response."""
    bias_res = await bias_check_chain(
        BiasCheckRequest(risk_description=response.revised_description)
    )

    extras: List[str] = []
    desc = response.revised_description.lower()
    original_desc = request.risk_description.lower()

    # Check both original and revised descriptions for biases
    if re.search(r"\bmay\b|\bcould\b|\bpossibly\b", desc):
        extras.append("ambiguous wording")

    # Check both original and revised descriptions for passive voice
    if re.search(r"\b(is|was|were|be|been|being|are)\b\s+\w+ed\b", desc) or re.search(
        r"\b(is|was|were|be|been|being|are)\b\s+\w+ed\b", original_desc
    ):
        extras.append("passive voice")

    if not re.search(r"\d", desc):
        extras.append("missing quantifiers")

    response.biases = list(set((bias_res.biases or []) + extras))
    return response


@register("check_definition")
async def check_definition_chain(
    request: DefinitionCheckRequest,
) -> DefinitionCheckResponse:
    """Check and improve risk definition."""
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
    # Handle missing language in BusinessContext
    language = (
        request.business_context.language.name
        if request.business_context.language is not None
        else "english"
    )
    inputs["language"] = language
    response = await chain.invoke(inputs)
    return await _process_response(response, request)
