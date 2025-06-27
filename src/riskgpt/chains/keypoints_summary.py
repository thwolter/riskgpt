from langchain_core.output_parsers import PydanticOutputParser

from riskgpt.chains.base import BaseChain
from riskgpt.helpers.prompt_loader import load_prompt
from riskgpt.models.chains.keypoints import (
    KeyPointSummaryRequest,
    KeyPointSummaryResponse,
)


async def keypoints_summary_chain(
    request: KeyPointSummaryRequest,
) -> KeyPointSummaryResponse:
    """
    Chain to generate text from key points with Harvard-style citations.

    This chain takes a list of KeyPoint objects and generates a coherent text
    that incorporates all the key points with proper Harvard-style citations.
    The output includes both the text with inline citations and a references
    section formatted in Harvard style.
    """
    prompt_data = load_prompt("keypoint_text")

    parser = PydanticOutputParser(pydantic_object=KeyPointSummaryResponse)
    chain = BaseChain(
        prompt_template=prompt_data["template"],
        parser=parser,
        prompt_name="keypoint_text",
    )

    # Format key points, handling multiple sources if available
    formatted_points = []
    for kp in request.key_points:
        sources = [kp.source_url] if kp.source_url else []
        if hasattr(kp, "additional_sources") and kp.additional_sources:
            sources.extend(kp.additional_sources)

        # Format with all available sources
        source_str = ", ".join([s for s in sources if s])
        formatted_points.append(f"- {kp.topic.value}: {kp.content} {source_str}")

    inputs = {"key_points": "\n".join(formatted_points)}
    return await chain.invoke(inputs)
