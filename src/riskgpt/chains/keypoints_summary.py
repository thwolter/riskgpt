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
    prompt_data = load_prompt("keypoint_summary")

    parser = PydanticOutputParser(pydantic_object=KeyPointSummaryResponse)
    chain = BaseChain(
        prompt_template=prompt_data["template"],
        parser=parser,
        prompt_name="keypoint_summary",
    )

    # Format key points with proper citations
    formatted_points = []
    for kp in request.key_points:
        citation = kp.get_inline_citation()
        citation_text = f" ({citation})" if citation else ""

        formatted_points.append(f"- {kp.topic.value}: {kp.content}{citation_text}")

    # Generate references section
    references = []
    for kp in request.key_points:
        if kp.citation:
            ref = kp.citation.format_harvard_reference()
            if ref not in references:
                references.append(ref)
        elif kp.source_url:
            # Fallback to simple URL-based reference
            from datetime import datetime
            from urllib.parse import urlparse

            domain = urlparse(kp.source_url).netloc
            current_date = datetime.now().strftime("%d %B %Y")
            ref = f"{domain}. [Online] Available at: {kp.source_url} [Accessed: {current_date}]"
            if ref not in references:
                references.append(ref)

    inputs = {
        "key_points": "\n".join(formatted_points),
        "references": "\n".join(references)
        if references
        else "No references available.",
    }
    return await chain.invoke(inputs)
