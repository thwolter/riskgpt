from typing import Any, Dict, Tuple

from langchain_core.output_parsers import PydanticOutputParser

from riskgpt.config.settings import RiskGPTSettings
from riskgpt.models.schemas import MonitoringRequest, MonitoringResponse
from riskgpt.registry.chain_registry import register
from riskgpt.utils.prompt_loader import load_prompt, load_system_prompt

from .base import BaseChain


def _prepare_monitoring_chain(
    request: MonitoringRequest,
) -> Tuple[BaseChain, Dict[str, Any]]:
    """Helper function to prepare the chain and inputs for both sync and async versions."""
    settings = RiskGPTSettings()
    prompt_data = load_prompt("get_monitoring")
    system_prompt = load_system_prompt()

    parser = PydanticOutputParser(pydantic_object=MonitoringResponse)
    chain = BaseChain(
        prompt_template=prompt_data["template"],
        parser=parser,
        settings=settings,
        prompt_name="get_monitoring",
    )

    inputs = request.model_dump()
    inputs["domain_section"] = (
        f"Domain knowledge: {request.business_context.domain_knowledge}"
        if request.business_context.domain_knowledge
        else ""
    )
    inputs["system_prompt"] = system_prompt

    return chain, inputs


@register("get_monitoring")
def get_monitoring_chain(request: MonitoringRequest) -> MonitoringResponse:
    """Get monitoring recommendations based on the provided request."""
    chain, inputs = _prepare_monitoring_chain(request)
    return chain.invoke(inputs)


async def async_get_monitoring_chain(request: MonitoringRequest) -> MonitoringResponse:
    """Asynchronous wrapper around :func:`get_monitoring_chain`."""
    chain, inputs = _prepare_monitoring_chain(request)
    return await chain.invoke_async(inputs)
