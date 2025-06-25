from typing import List

from langchain_core.output_parsers import PydanticOutputParser

from src.models.workflows.context import KeyPoint, KeyPointTextResponse
from src.utils.prompt_loader import load_prompt

from .base import BaseChain


class KeyPointTextRequest:
    """Request model for generating text from key points."""

    def __init__(self, key_points: List[KeyPoint]):
        self.key_points = key_points

    def model_dump(self, **kwargs):
        """Convert to dictionary for chain input."""
        return {"key_points": [kp.model_dump() for kp in self.key_points]}


async def keypoint_text_chain(
    key_points: List[KeyPoint],
) -> KeyPointTextResponse:
    """
    Chain to generate text from key points with Harvard-style citations.

    This chain takes a list of KeyPoint objects and generates a coherent text
    that incorporates all the key points with proper Harvard-style citations.
    The output includes both the text with inline citations and a references
    section formatted in Harvard style.

    Args:
        key_points: List of KeyPoint objects containing content and source information

    Returns:
        KeyPointTextResponse with generated text and references
    """
    prompt_data = load_prompt("keypoint_text")

    parser = PydanticOutputParser(pydantic_object=KeyPointTextResponse)
    chain = BaseChain(
        prompt_template=prompt_data["template"],
        parser=parser,
        prompt_name="keypoint_text",
    )

    inputs = {
        "key_points": "\n".join(
            [f"- {kp.topic.value}: {kp.content} {kp.source_url}" for kp in key_points]
        )
    }
    return await chain.invoke(inputs)
