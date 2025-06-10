from typing import Any, Dict, Tuple

from langchain_core.output_parsers import PydanticOutputParser

from riskgpt.config.settings import RiskGPTSettings
from riskgpt.models.schemas import AssessmentRequest, AssessmentResponse
from riskgpt.registry.chain_registry import register
from riskgpt.utils.prompt_loader import load_prompt, load_system_prompt

from .base import BaseChain


def _prepare_assessment_chain(
    request: AssessmentRequest,
) -> Tuple[BaseChain, Dict[str, Any]]:
    """Helper function to prepare the chain and inputs for both sync and async versions."""
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
    return chain, inputs


@register("get_assessment")
def get_assessment_chain(request: AssessmentRequest) -> AssessmentResponse:
    """Get assessment based on the provided request."""
    chain, inputs = _prepare_assessment_chain(request)
    return chain.invoke(inputs)


async def async_get_assessment_chain(request: AssessmentRequest) -> AssessmentResponse:
    """Asynchronous version of the get_assessment_chain."""
    chain, inputs = _prepare_assessment_chain(request)
    return await chain.invoke_async(inputs)
