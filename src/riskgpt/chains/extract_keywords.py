"""Extract keywords chain implementation."""

from langchain_core.output_parsers import PydanticOutputParser

from riskgpt.chains.base import BaseChain
from riskgpt.models.chains.keywords import (
    ExtractKeywordsRequest,
    ExtractKeywordsResponse,
)


async def extract_keywords_chain(
    request: ExtractKeywordsRequest,
) -> ExtractKeywordsResponse:
    """Extract key search terms from a long query.

    Args:
        request: The request containing the query text and max_keywords

    Returns:
        A response containing the extracted keywords
    """
    parser = PydanticOutputParser(pydantic_object=ExtractKeywordsResponse)

    # Define the prompt template
    prompt_template = (
        "Extract the {max_keywords} most important keywords or phrases for a semantic search from the following text. "
        "Return only the keywords separated by spaces, with no numbering or additional text:\n\n{query}\n\n"
        "{format_instructions}"
    )

    chain = BaseChain(
        prompt_template=prompt_template,
        parser=parser,
        prompt_name="extract_keywords",
    )

    inputs = request.model_dump(mode="json", exclude_none=True)
    result = await chain.invoke(inputs)
    return result
