from langchain_core.output_parsers import PydanticOutputParser

from riskgpt.models.chains.monitoring import MonitoringRequest, MonitoringResponse
from riskgpt.registry.chain_registry import register
from riskgpt.utils.prompt_loader import load_prompt

from .base import BaseChain


@register("monitoring")
async def get_monitoring_chain(request: MonitoringRequest) -> MonitoringResponse:
    """Chain to get monitoring information based on the request."""

    prompt_data = load_prompt("get_monitoring")

    parser = PydanticOutputParser(pydantic_object=MonitoringResponse)
    chain = BaseChain(
        prompt_template=prompt_data["template"],
        parser=parser,
        prompt_name="get_monitoring",
    )

    inputs = request.model_dump(mode="json", exclude_none=True)
    return await chain.invoke(inputs)
