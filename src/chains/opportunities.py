from langchain_core.output_parsers import PydanticOutputParser

from src.models.chains.opportunity import OpportunityRequest, OpportunityResponse
from src.utils.prompt_loader import load_prompt

from src.chains.base import BaseChain


async def opportunities_chain(
    request: OpportunityRequest,
) -> OpportunityResponse:
    prompt_data = load_prompt("opportunities")

    parser = PydanticOutputParser(pydantic_object=OpportunityResponse)
    chain = BaseChain(
        prompt_template=prompt_data["template"],
        parser=parser,
        prompt_name="opportunities",
    )

    inputs = request.model_dump(mode="json", exclude_none=True)
    return await chain.invoke(inputs)
