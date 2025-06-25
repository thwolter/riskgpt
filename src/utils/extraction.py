from typing import Any, Dict

from langchain_core.output_parsers import PydanticOutputParser

from src.chains.base import BaseChain
from src.models.workflows.context import ExtractKeyPointsResponse
from src.utils.prompt_loader import load_prompt


async def extract_key_points(
    source: Dict[str, Any],
    source_type: str,
) -> ExtractKeyPointsResponse:
    """
    Extract key points from a source using an LLM.

    Args:
        source: The source dictionary containing title, comment, etc.
        source_type: The type of source (news, professional, regulatory, peer)

    Returns:
        Tuple containing:
        - List of extracted key points
        - ResponseInfo with token usage and cost information
    """
    title = source.get("title", "")
    comment = source.get("comment", "")
    content = f"Title: {title}\n\nContent: {comment}"

    parser = PydanticOutputParser(pydantic_object=ExtractKeyPointsResponse)

    prompt_data = load_prompt("extract_key_points")

    chain = BaseChain(
        prompt_template=prompt_data["template"],
        parser=parser,
        prompt_name=f"extract_{source_type}_key_points",
    )

    result = await chain.invoke({"source_type": source_type, "content": content})
    return result
