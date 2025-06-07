from langchain_core.output_parsers import PydanticOutputParser

from riskgpt.utils.prompt_loader import load_prompt
from riskgpt.config.settings import RiskGPTSettings
from riskgpt.models.schemas import ImpactRequest, ImpactResponse
from riskgpt.registry.chain_registry import register
from .base import BaseChain


@register("get_impact")
def get_impact_chain(request: ImpactRequest) -> ImpactResponse:
    settings = RiskGPTSettings()
    prompt_data = load_prompt("get_impact")

    parser = PydanticOutputParser(pydantic_object=ImpactResponse)
    chain = BaseChain(
        prompt_template=prompt_data["template"],
        parser=parser,
        settings=settings,
        prompt_name="get_impact",
    )

    inputs = request.model_dump()
    inputs["domain_section"] = (
        f"Domain knowledge: {request.domain_knowledge}" if request.domain_knowledge else ""
    )

    return chain.invoke(inputs)
