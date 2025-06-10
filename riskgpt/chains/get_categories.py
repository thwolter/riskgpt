from typing import Any, Dict, Tuple

from langchain_core.output_parsers import PydanticOutputParser

from riskgpt.config.settings import RiskGPTSettings
from riskgpt.models.schemas import CategoryRequest, CategoryResponse
from riskgpt.registry.chain_registry import register
from riskgpt.utils.prompt_loader import load_prompt

from .base import BaseChain


def _prepare_categories_chain(
    request: CategoryRequest,
) -> Tuple[BaseChain, Dict[str, Any]]:
    """Helper function to prepare the chain and inputs for both sync and async versions."""
    settings = RiskGPTSettings()
    prompt_data = load_prompt("get_categories")

    parser = PydanticOutputParser(pydantic_object=CategoryResponse)
    chain = BaseChain(
        prompt_template=prompt_data["template"],
        parser=parser,
        settings=settings,
        prompt_name="get_categories",
    )

    inputs = request.model_dump()
    # Extract fields from business_context and add them directly to inputs
    inputs["project_description"] = request.business_context.project_description
    inputs["language"] = request.business_context.language

    inputs["domain_section"] = (
        f"Domain knowledge: {request.business_context.domain_knowledge}"
        if request.business_context.domain_knowledge
        else ""
    )
    inputs["existing_categories_section"] = (
        f"Existing categories: {', '.join(request.existing_categories)}"
        if request.existing_categories
        else ""
    )

    return chain, inputs


@register("get_categories")
def get_categories_chain(request: CategoryRequest) -> CategoryResponse:
    """Get risk categories based on the provided request."""
    chain, inputs = _prepare_categories_chain(request)
    return chain.invoke(inputs)


async def async_get_categories_chain(request: CategoryRequest) -> CategoryResponse:
    """Asynchronous wrapper around :func:`get_categories_chain`."""
    chain, inputs = _prepare_categories_chain(request)
    return await chain.invoke_async(inputs)
