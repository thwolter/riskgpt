from langchain_core.output_parsers import PydanticOutputParser

from riskgpt.utils.prompt_loader import load_prompt
from riskgpt.config.settings import RiskGPTSettings
from riskgpt.models.schemas import RiskRequest, RiskResponse
from riskgpt.registry.chain_registry import register
from .base import BaseChain


@register("get_risks")
def get_risks_chain(request: RiskRequest) -> RiskResponse:
    settings = RiskGPTSettings()
    prompt_data = load_prompt("get_risks")

    parser = PydanticOutputParser(pydantic_object=RiskResponse)
    chain = BaseChain(
        prompt_template=prompt_data["template"],
        parser=parser,
        settings=settings,
        prompt_name="get_risks",
    )

    inputs = request.model_dump()
    inputs["domain_section"] = (
        f"Domain knowledge: {request.domain_knowledge}" if request.domain_knowledge else ""
    )

    return chain.invoke(inputs)
