from langchain_core.output_parsers import PydanticOutputParser

from src.models.chains.risk import RiskRequest, RiskResponse
from src.utils.prompt_loader import load_prompt

from .base import BaseChain


async def risk_identification_chain(request: RiskRequest) -> RiskResponse:
    prompt_data = load_prompt("get_risks")

    parser = PydanticOutputParser(pydantic_object=RiskResponse)
    chain = BaseChain(
        prompt_template=prompt_data["template"],
        parser=parser,
        prompt_name="get_risks",
    )

    inputs = request.model_dump(mode="json", exclude_none=True)
    return await chain.invoke(inputs)
