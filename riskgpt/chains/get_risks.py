from langchain_core.output_parsers import PydanticOutputParser

from riskgpt.models.chains.risk import RiskRequest, RiskResponse
from riskgpt.registry.chain_registry import register
from riskgpt.utils.prompt_loader import load_prompt

from .base import BaseChain


@register("get_risks")
async def get_risks_chain(request: RiskRequest) -> RiskResponse:
    prompt_data = load_prompt("get_risks")

    parser = PydanticOutputParser(pydantic_object=RiskResponse)
    chain = BaseChain(
        prompt_template=prompt_data["template"],
        parser=parser,
        prompt_name="get_risks",
    )

    inputs = request.model_dump(mode="json", exclude_none=True)
    return await chain.invoke(inputs)
