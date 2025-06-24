from typing import Any, Dict, List, Tuple

from langchain_core.output_parsers import PydanticOutputParser
from pydantic import Field

from src.chains.base import BaseChain
from src.models.base import BaseResponse, ResponseInfo


class KeyPoints(BaseResponse):
    """Model for key points extracted from a source."""

    points: List[str] = Field(
        description="List of key points extracted from the source"
    )


async def extract_key_points(
    source: Dict[str, Any],
    source_type: str,
) -> Tuple[List[str], ResponseInfo]:
    """
    Extract key points from a source using an LLM.

    Args:
        source: The source dictionary containing title, comment, etc.
        source_type: The type of source (news, professional, regulatory, peer)
        settings: Optional RiskGPTSettings

    Returns:
        Tuple containing:
        - List of extracted key points
        - ResponseInfo with token usage and cost information
    """
    title = source.get("title", "")
    comment = source.get("comment", "")
    content = f"Title: {title}\n\nContent: {comment}"

    parser = PydanticOutputParser(pydantic_object=KeyPoints)

    prompt_template = """
    You are an expert at extracting key points from {source_type} sources.

    Please analyze the following {source_type} source and extract the most important key points.
    Focus on facts, insights, and implications that would be relevant for risk assessment.

    {content}

    {format_instructions}
    """

    chain = BaseChain(
        prompt_template=prompt_template,
        parser=parser,
        prompt_name=f"extract_{source_type}_key_points",
    )

    result = await chain.invoke({"source_type": source_type, "content": content})

    return result.points, result.response_info
