from langchain_core.output_parsers import PydanticOutputParser

from riskgpt.models.chains.assessment import AssessmentRequest, AssessmentResponse
from riskgpt.registry.chain_registry import register
from riskgpt.utils.prompt_loader import load_prompt

from .base import BaseChain


@register("get_assessment")
async def get_assessment_chain(request: AssessmentRequest) -> AssessmentResponse:
    """Get assessment based on the provided request."""

    prompt_data = load_prompt("get_assessment")

    parser = PydanticOutputParser(pydantic_object=AssessmentResponse)
    chain = BaseChain(
        prompt_template=prompt_data["template"],
        parser=parser,
        prompt_name="get_assessment",
    )

    inputs = request.model_dump(mode="json", exclude_none=True)
    return await chain.invoke(inputs)
