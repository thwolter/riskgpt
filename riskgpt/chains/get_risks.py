from langchain_core.output_parsers import PydanticOutputParser

from riskgpt.config.settings import RiskGPTSettings
from riskgpt.models.schemas import RiskRequest, RiskResponse
from riskgpt.registry.chain_registry import register
from riskgpt.utils.prompt_loader import load_prompt, load_system_prompt

from .base import BaseChain


@register("get_risks")
def get_risks_chain(request: RiskRequest) -> RiskResponse:
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

    return chain.invoke(inputs)


async def async_get_risks_chain(request: RiskRequest) -> RiskResponse:
    """Asynchronous wrapper around :func:`get_risks_chain`."""
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

    return await chain.invoke_async(inputs)
