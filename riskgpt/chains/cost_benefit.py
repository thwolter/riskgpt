from typing import Any, Dict, Tuple

from langchain_core.output_parsers import PydanticOutputParser

from riskgpt.config.settings import RiskGPTSettings
from riskgpt.models.schemas import CostBenefitRequest, CostBenefitResponse
from riskgpt.registry.chain_registry import register
from riskgpt.utils.prompt_loader import load_prompt, load_system_prompt

from .base import BaseChain


def _prepare_cost_benefit_chain(
    request: CostBenefitRequest,
) -> Tuple[BaseChain, Dict[str, Any]]:
    """Helper function to prepare the chain and inputs for both sync and async versions."""
    settings = RiskGPTSettings()
    prompt_data = load_prompt("cost_benefit")
    system_prompt = load_system_prompt()

    parser = PydanticOutputParser(pydantic_object=CostBenefitResponse)
    chain = BaseChain(
        prompt_template=prompt_data["template"],
        parser=parser,
        settings=settings,
        prompt_name="cost_benefit",
    )

    inputs = request.model_dump()
    inputs["mitigations"] = ", ".join(request.mitigations)
    inputs["domain_section"] = (
        f"Domain knowledge: {request.domain_knowledge}"
        if request.domain_knowledge
        else ""
    )
    inputs["system_prompt"] = system_prompt

    return chain, inputs


@register("cost_benefit")
def cost_benefit_chain(request: CostBenefitRequest) -> CostBenefitResponse:
    """Perform cost-benefit analysis on mitigations."""
    chain, inputs = _prepare_cost_benefit_chain(request)
    return chain.invoke(inputs)


async def async_cost_benefit_chain(request: CostBenefitRequest) -> CostBenefitResponse:
    """Asynchronous wrapper around :func:`cost_benefit_chain`."""
    chain, inputs = _prepare_cost_benefit_chain(request)
    return await chain.invoke_async(inputs)
