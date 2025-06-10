from typing import Any, Dict, Tuple

from langchain_core.output_parsers import PydanticOutputParser

from riskgpt.config.settings import RiskGPTSettings
from riskgpt.models.schemas import RiskRequest, RiskResponse
from riskgpt.registry.chain_registry import register
from riskgpt.utils.prompt_loader import load_prompt, load_system_prompt

from .base import BaseChain


def _prepare_risks_chain(request: RiskRequest) -> Tuple[BaseChain, Dict[str, Any]]:
    """Helper function to prepare the chain and inputs for both sync and async versions."""
    settings = RiskGPTSettings()
    prompt_data = load_prompt("get_risks")
    system_prompt = load_system_prompt()

    parser = PydanticOutputParser(pydantic_object=RiskResponse)
    chain = BaseChain(
        prompt_template=prompt_data["template"],
        parser=parser,
        settings=settings,
        prompt_name="get_risks",
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
    inputs["existing_risks_section"] = (
        f"Existing risks: {', '.join(request.existing_risks)}"
        if request.existing_risks
        else ""
    )
    inputs["system_prompt"] = system_prompt

    return chain, inputs


@register("get_risks")
def get_risks_chain(request: RiskRequest) -> RiskResponse:
    """Get risks based on the provided request."""
    chain, inputs = _prepare_risks_chain(request)
    return chain.invoke(inputs)


async def async_get_risks_chain(request: RiskRequest) -> RiskResponse:
    """Asynchronous version of the get_risks_chain."""
    chain, inputs = _prepare_risks_chain(request)
    return await chain.invoke_async(inputs)
