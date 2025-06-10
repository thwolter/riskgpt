from typing import Any, Dict, Tuple

from langchain_core.output_parsers import PydanticOutputParser

from riskgpt.config.settings import RiskGPTSettings
from riskgpt.models.schemas import PrioritizationRequest, PrioritizationResponse
from riskgpt.registry.chain_registry import register
from riskgpt.utils.prompt_loader import load_prompt, load_system_prompt

from .base import BaseChain


def _prepare_prioritize_risks_chain(
    request: PrioritizationRequest,
) -> Tuple[BaseChain, Dict[str, Any]]:
    """Helper function to prepare the chain and inputs for both sync and async versions."""
    settings = RiskGPTSettings()
    prompt_data = load_prompt("prioritize_risks")
    system_prompt = load_system_prompt()

    parser = PydanticOutputParser(pydantic_object=PrioritizationResponse)
    chain = BaseChain(
        prompt_template=prompt_data["template"],
        parser=parser,
        settings=settings,
        prompt_name="prioritize_risks",
    )

    inputs = request.model_dump()
    inputs["risks"] = ", ".join(request.risks)
    inputs["domain_section"] = (
        f"Domain knowledge: {request.business_context.domain_knowledge} "
        if request.business_context.domain_knowledge
        else ""
    )
    inputs["system_prompt"] = system_prompt

    return chain, inputs


@register("prioritize_risks")
def prioritize_risks_chain(request: PrioritizationRequest) -> PrioritizationResponse:
    """Prioritize risks based on the provided request."""
    chain, inputs = _prepare_prioritize_risks_chain(request)
    return chain.invoke(inputs)


async def async_prioritize_risks_chain(
    request: PrioritizationRequest,
) -> PrioritizationResponse:
    """Asynchronous wrapper around :func:`prioritize_risks_chain`."""
    chain, inputs = _prepare_prioritize_risks_chain(request)
    return await chain.invoke_async(inputs)
