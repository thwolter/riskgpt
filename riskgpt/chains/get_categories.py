from langchain_core.output_parsers import PydanticOutputParser

from riskgpt.models.chains.categorization import CategoryRequest, CategoryResponse
from riskgpt.registry.chain_registry import register
from riskgpt.utils.prompt_loader import load_prompt

from .base import BaseChain


@register("get_categories")
async def get_categories_chain(request: CategoryRequest) -> CategoryResponse:
    """Asynchronous wrapper around :func:`get_categories_chain`."""
    prompt_data = load_prompt("get_categories")

    parser = PydanticOutputParser(pydantic_object=CategoryResponse)
    chain = BaseChain(
        prompt_template=prompt_data["template"],
        parser=parser,
        prompt_name="get_categories",
    )

    inputs = request.model_dump(mode="json", exclude_none=True)
    return await chain.invoke(inputs)
