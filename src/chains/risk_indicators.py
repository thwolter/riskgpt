from langchain_core.output_parsers import PydanticOutputParser

from src.chains.base import BaseChain
from src.models.chains.monitoring import RiskIndicatorRequest, RiskIndicatorResponse
from src.utils.prompt_loader import load_prompt


async def risk_indicators_chain(request: RiskIndicatorRequest) -> RiskIndicatorResponse:
    """Chain to get monitoring information based on the request."""

    prompt_data = load_prompt("risk_indicators")

    parser = PydanticOutputParser(pydantic_object=RiskIndicatorResponse)
    chain = BaseChain(
        prompt_template=prompt_data["template"],
        parser=parser,
        prompt_name="risk_indicators",
    )

    inputs = request.model_dump(mode="json", exclude_none=True)
    return await chain.invoke(inputs)
