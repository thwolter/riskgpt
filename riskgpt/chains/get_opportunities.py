from langchain_core.output_parsers import PydanticOutputParser

from riskgpt.config.settings import RiskGPTSettings
from riskgpt.models.schemas import OpportunityRequest, OpportunityResponse
from riskgpt.registry.chain_registry import register
from riskgpt.utils.prompt_loader import load_prompt, load_system_prompt

from .base import BaseChain


@register("get_opportunities")
def get_opportunities_chain(request: OpportunityRequest) -> OpportunityResponse:
    settings = RiskGPTSettings()
    prompt_data = load_prompt("get_opportunities")
    system_prompt = load_system_prompt()

    parser = PydanticOutputParser(pydantic_object=OpportunityResponse)
    chain = BaseChain(
        prompt_template=prompt_data["template"],
        parser=parser,
        settings=settings,
        prompt_name="get_opportunities",
    )

    inputs = request.model_dump()
    inputs["risks"] = ", ".join(request.risks)
    inputs["domain_section"] = (
        f"Domain knowledge: {request.domain_knowledge}"
        if request.domain_knowledge
        else ""
    )
    inputs["system_prompt"] = system_prompt

    return chain.invoke(inputs)


async def async_get_opportunities_chain(
    request: OpportunityRequest,
) -> OpportunityResponse:
    """Asynchronous wrapper around :func:`get_opportunities_chain`."""
    settings = RiskGPTSettings()
    prompt_data = load_prompt("get_opportunities")
    system_prompt = load_system_prompt()

    parser = PydanticOutputParser(pydantic_object=OpportunityResponse)
    chain = BaseChain(
        prompt_template=prompt_data["template"],
        parser=parser,
        settings=settings,
        prompt_name="get_opportunities",
    )

    inputs = request.model_dump()
    inputs["risks"] = ", ".join(request.risks)
    inputs["domain_section"] = (
        f"Domain knowledge: {request.domain_knowledge}"
        if request.domain_knowledge
        else ""
    )
    inputs["system_prompt"] = system_prompt

    return await chain.invoke_async(inputs)
