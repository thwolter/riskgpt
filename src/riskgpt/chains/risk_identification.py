from langchain_core.output_parsers import PydanticOutputParser

from riskgpt.chains.base import BaseChain
from riskgpt.helpers.prompt_loader import load_prompt
from riskgpt.models.chains.risk import (
    RisksIdentificationRequest,
    RisksIdentificationResponse,
)


async def risk_identification_chain(
    request: RisksIdentificationRequest,
) -> RisksIdentificationResponse:
    prompt_data = load_prompt("risk_identification")

    parser = PydanticOutputParser(pydantic_object=RisksIdentificationResponse)
    chain = BaseChain(
        prompt_template=prompt_data["template"],
        parser=parser,
        prompt_name="risk_identification",
    )

    inputs = request.model_dump(mode="json", exclude_none=True)
    return await chain.invoke(inputs)
