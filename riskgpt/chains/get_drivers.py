from langchain_core.output_parsers import PydanticOutputParser

from riskgpt.utils.prompt_loader import load_prompt, load_system_prompt
from riskgpt.config.settings import RiskGPTSettings
from riskgpt.models.schemas import DriverRequest, DriverResponse
from riskgpt.registry.chain_registry import register
from .base import BaseChain


@register("get_drivers")
def get_drivers_chain(request: DriverRequest) -> DriverResponse:
    settings = RiskGPTSettings()
    prompt_data = load_prompt("get_drivers")
    system_prompt = load_system_prompt()

    parser = PydanticOutputParser(pydantic_object=DriverResponse)
    chain = BaseChain(
        prompt_template=prompt_data["template"],
        parser=parser,
        settings=settings,
        prompt_name="get_drivers",
    )

    inputs = request.model_dump()
    inputs["domain_section"] = (
        f"Domain knowledge: {request.domain_knowledge}" if request.domain_knowledge else ""
    )
    inputs["system_prompt"] = system_prompt

    return chain.invoke(inputs)


async def async_get_drivers_chain(request: DriverRequest) -> DriverResponse:
    """Asynchronous wrapper around :func:`get_drivers_chain`."""
    settings = RiskGPTSettings()
    prompt_data = load_prompt("get_drivers")
    system_prompt = load_system_prompt()

    parser = PydanticOutputParser(pydantic_object=DriverResponse)
    chain = BaseChain(
        prompt_template=prompt_data["template"],
        parser=parser,
        settings=settings,
        prompt_name="get_drivers",
    )

    inputs = request.model_dump()
    inputs["domain_section"] = (
        f"Domain knowledge: {request.domain_knowledge}" if request.domain_knowledge else ""
    )
    inputs["system_prompt"] = system_prompt

    return await chain.invoke_async(inputs)
