from langchain_core.output_parsers import PydanticOutputParser

from src.models.chains.monitoring import MonitoringRequest, MonitoringResponse
from src.registry.chain_registry import register
from src.utils.prompt_loader import load_prompt

from .base import BaseChain


@register("risk_monitoring")
async def risk_indicators_chain(request: MonitoringRequest) -> MonitoringResponse:
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
