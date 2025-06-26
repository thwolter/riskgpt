from langchain_core.output_parsers import PydanticOutputParser

from src.models.chains.assessment import AssessmentRequest, AssessmentResponse
from src.utils.prompt_loader import load_prompt

from src.chains.base import BaseChain


async def risk_assessment_chain(request: AssessmentRequest) -> AssessmentResponse:
    """Get assessment based on the provided request."""

    prompt_data = load_prompt("risk_assessment")

    parser = PydanticOutputParser(pydantic_object=AssessmentResponse)
    chain = BaseChain(
        prompt_template=prompt_data["template"],
        parser=parser,
        prompt_name="risk_assessment",
    )

    inputs = request.model_dump(mode="json", exclude_none=True)
    return await chain.invoke(inputs)
