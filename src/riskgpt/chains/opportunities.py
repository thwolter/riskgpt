from langchain_core.output_parsers import PydanticOutputParser

from src.riskgpt.chains.base import BaseChain
from src.riskgpt.models.chains.opportunity import (
    OpportunityRequest,
    OpportunityResponse,
)
from src.riskgpt.utils.prompt_loader import load_prompt


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
