from __future__ import annotations

from typing import Dict

from langchain_core.output_parsers import PydanticOutputParser

from riskgpt.chains.base import BaseChain
from riskgpt.config.settings import RiskGPTSettings
from riskgpt.models.schemas import ContextQualityRequest, ContextQualityResponse
from riskgpt.utils.prompt_loader import load_prompt, load_system_prompt


def check_context_quality(request: ContextQualityRequest) -> ContextQualityResponse:
    """Evaluate quality of provided project context knowledge."""

    settings = RiskGPTSettings()
    prompt_data = load_prompt("check_context_quality")
    system_prompt = load_system_prompt()
    parser = PydanticOutputParser(pydantic_object=ContextQualityResponse)
    chain = BaseChain(
        prompt_template=prompt_data["template"],
        parser=parser,
        settings=settings,
        prompt_name="check_context_quality",
    )

    inputs: Dict[str, str] = request.model_dump()
    # Extract fields from business_context and add them directly to inputs
    inputs["context_knowledge"] = request.business_context.domain_knowledge or ""
    inputs["language"] = request.business_context.language or "en"
    inputs["system_prompt"] = system_prompt
    return chain.invoke(inputs)
