from __future__ import annotations

import re
from typing import List

from riskgpt.models.schemas import BiasCheckRequest, BiasCheckResponse
from riskgpt.registry.chain_registry import register


@register("bias_check")
def bias_check_chain(request: BiasCheckRequest) -> BiasCheckResponse:
    desc = request.risk_description.lower()
    biases: List[str] = []
    suggestions: List[str] = []

    if re.search(r"\balways\b|\bnever\b", desc):
        biases.append("framing")
        suggestions.append("Avoid absolute terms like 'always' or 'never'.")

    if re.search(r"\brecent\b|\blatest\b", desc):
        biases.append("availability")
        suggestions.append(
            "Check whether recent events unduly influence the assessment."
        )

    return BiasCheckResponse(
        biases=list(set(biases)), suggestions="; ".join(suggestions)
    )


async def async_bias_check_chain(request: BiasCheckRequest) -> BiasCheckResponse:
    return bias_check_chain(request)
