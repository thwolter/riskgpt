from langchain_core.output_parsers import PydanticOutputParser

from src.models.chains.mitigation import MitigationRequest, MitigationResponse
from src.utils.prompt_loader import load_prompt

from .base import BaseChain


@register("risk_mitigations")
async def risk_mitigations_chain(request: MitigationRequest) -> MitigationResponse:
    """
    Get mitigations for a given risk.
    """
    prompt_data = load_prompt("get_mitigations")

    parser = PydanticOutputParser(pydantic_object=MitigationResponse)
    chain = BaseChain(
        prompt_template=prompt_data["template"],
        parser=parser,
        prompt_name="get_mitigations",
    )

    inputs = request.model_dump(mode="json", exclude_none=True)
    return await chain.invoke(inputs)
