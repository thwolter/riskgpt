from langchain_core.output_parsers import PydanticOutputParser

from src.models.chains.drivers import DriverRequest, DriverResponse
from src.utils.prompt_loader import load_prompt

from src.chains.base import BaseChain


async def risk_drivers_chain(request: DriverRequest) -> DriverResponse:
    """
    Get risk drivers based on the provided request.
    This function uses a prompt template to generate a response containing risk drivers
    based on the business context and risk description provided in the request.
    """

    prompt_data = load_prompt("risk_drivers")

    parser = PydanticOutputParser(pydantic_object=DriverResponse)
    chain = BaseChain(
        prompt_template=prompt_data["template"],
        parser=parser,
        prompt_name="risk_drivers",
    )

    inputs = request.model_dump(mode="json", exclude_none=True)
    return await chain.invoke(inputs)
