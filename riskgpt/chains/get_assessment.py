from langchain_core.output_parsers import PydanticOutputParser

from riskgpt.utils.prompt_loader import load_prompt, load_system_prompt
from riskgpt.config.settings import RiskGPTSettings
from riskgpt.models.schemas import AssessmentRequest, AssessmentResponse
from riskgpt.registry.chain_registry import register
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
    inputs["domain_section"] = (
        f"Domain knowledge: {request.domain_knowledge}" if request.domain_knowledge else ""
    )

    inputs["system_prompt"] = system_prompt
    return chain.invoke(inputs)
