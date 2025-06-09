from langchain_core.output_parsers import PydanticOutputParser

from riskgpt.config.settings import RiskGPTSettings
from riskgpt.models.schemas import CommunicationRequest, CommunicationResponse
from riskgpt.registry.chain_registry import register
from riskgpt.utils.prompt_loader import load_prompt, load_system_prompt

from .base import BaseChain


@register("communicate_risks")
def communicate_risks_chain(request: CommunicationRequest) -> CommunicationResponse:
    settings = RiskGPTSettings()
    prompt_data = load_prompt("communicate_risks")
    system_prompt = load_system_prompt()

    parser = PydanticOutputParser(pydantic_object=CommunicationResponse)
    chain = BaseChain(
        prompt_template=prompt_data["template"],
        parser=parser,
        settings=settings,
        prompt_name="communicate_risks",
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
    inputs["system_prompt"] = system_prompt

    return chain.invoke(inputs)


async def async_communicate_risks_chain(
    request: CommunicationRequest,
) -> CommunicationResponse:
    """Asynchronous wrapper around :func:`communicate_risks_chain`."""
    settings = RiskGPTSettings()
    prompt_data = load_prompt("communicate_risks")
    system_prompt = load_system_prompt()

    parser = PydanticOutputParser(pydantic_object=CommunicationResponse)
    chain = BaseChain(
        prompt_template=prompt_data["template"],
        parser=parser,
        settings=settings,
        prompt_name="communicate_risks",
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
    inputs["system_prompt"] = system_prompt

    return await chain.invoke_async(inputs)
