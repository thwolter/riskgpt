from langchain_core.output_parsers import PydanticOutputParser

from riskgpt.config.settings import RiskGPTSettings
from riskgpt.models.schemas import AssessmentRequest, AssessmentResponse
from riskgpt.registry.chain_registry import register
from riskgpt.utils.prompt_loader import load_prompt, load_system_prompt

from .base import BaseChain


@register("get_assessment")
def get_assessment_chain(request: AssessmentRequest) -> AssessmentResponse:
    settings = RiskGPTSettings()
    prompt_data = load_prompt("get_assessment")
    system_prompt = load_system_prompt()

    parser = PydanticOutputParser(pydantic_object=AssessmentResponse)
    chain = BaseChain(
        prompt_template=prompt_data["template"],
        parser=parser,
        settings=settings,
        prompt_name="get_assessment",
    )

    inputs = request.model_dump()
    # Extract fields from business_context and add them directly to inputs
    inputs["project_description"] = request.business_context.project_description
    inputs["language"] = request.business_context.language

    inputs["domain_section"] = request.business_context.get_domain_section()

    inputs["system_prompt"] = system_prompt
    return chain.invoke(inputs)


async def async_get_assessment_chain(request: AssessmentRequest) -> AssessmentResponse:
    """Asynchronous wrapper around :func:`get_assessment_chain`."""
    settings = RiskGPTSettings()
    prompt_data = load_prompt("get_assessment")
    system_prompt = load_system_prompt()

    parser = PydanticOutputParser(pydantic_object=AssessmentResponse)
    chain = BaseChain(
        prompt_template=prompt_data["template"],
        parser=parser,
        settings=settings,
        prompt_name="get_assessment",
    )

    inputs = request.model_dump()
    # Extract fields from business_context and add them directly to inputs
    inputs["project_description"] = request.business_context.project_description
    inputs["language"] = request.business_context.language

    inputs["domain_section"] = request.business_context.get_domain_section()

    inputs["system_prompt"] = system_prompt
    return await chain.invoke_async(inputs)
