from typing import Any, Dict, Tuple

from langchain_core.output_parsers import PydanticOutputParser

from riskgpt.config.settings import RiskGPTSettings
from riskgpt.models.schemas import MitigationRequest, MitigationResponse
from riskgpt.registry.chain_registry import register
from riskgpt.utils.prompt_loader import load_prompt, load_system_prompt

from .base import BaseChain


def _prepare_mitigations_chain(
    request: MitigationRequest,
) -> Tuple[BaseChain, Dict[str, Any]]:
    """Helper function to prepare the chain and inputs for both sync and async versions."""
    settings = RiskGPTSettings()
    prompt_data = load_prompt("get_mitigations")
    system_prompt = load_system_prompt()

    parser = PydanticOutputParser(pydantic_object=MitigationResponse)
    chain = BaseChain(
        prompt_template=prompt_data["template"],
        parser=parser,
        settings=settings,
        prompt_name="get_mitigations",
    )

    inputs = request.model_dump()
    # Extract fields from business_context and add them directly to inputs
    inputs["project_description"] = request.business_context.project_description
    inputs["language"] = request.business_context.language

    inputs["domain_section"] = (
        f"Domain knowledge: {request.business_context.domain_knowledge}"
        if request.business_context.domain_knowledge
        else ""
    )
    inputs["drivers_section"] = (
        f"Identified risk drivers: {', '.join(request.drivers)}"
        if request.drivers
        else ""
    )
    inputs["system_prompt"] = system_prompt

    return chain, inputs


@register("get_mitigations")
def get_mitigations_chain(request: MitigationRequest) -> MitigationResponse:
    """Get mitigations for identified risks."""
    chain, inputs = _prepare_mitigations_chain(request)
    return chain.invoke(inputs)


async def async_get_mitigations_chain(request: MitigationRequest) -> MitigationResponse:
    """Asynchronous wrapper around :func:`get_mitigations_chain`."""
    chain, inputs = _prepare_mitigations_chain(request)
    return await chain.invoke_async(inputs)
