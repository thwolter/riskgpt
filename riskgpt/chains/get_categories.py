from langchain_core.output_parsers import PydanticOutputParser

from riskgpt.config.settings import RiskGPTSettings
from riskgpt.models.schemas import CategoryRequest, CategoryResponse
from riskgpt.registry.chain_registry import register
from riskgpt.utils.prompt_loader import load_prompt

from .base import BaseChain


@register("get_categories")
def get_categories_chain(request: CategoryRequest) -> CategoryResponse:
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

    return chain.invoke(inputs)


async def async_get_categories_chain(request: CategoryRequest) -> CategoryResponse:
    """Asynchronous wrapper around :func:`get_categories_chain`."""
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

    return await chain.invoke_async(inputs)
