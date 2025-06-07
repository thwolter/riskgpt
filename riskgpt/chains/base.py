from __future__ import annotations

from typing import Any, Dict, Optional

from langchain_community.callbacks import get_openai_callback
from langchain_community.llms import FakeListLLM
from langchain_core.output_parsers import BaseOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from riskgpt.config.settings import RiskGPTSettings
from riskgpt.logger import logger
from riskgpt.models.schemas import ResponseInfo
from riskgpt.utils.memory_factory import get_memory


class BaseChain:
    """Reusable chain setup for prompt -> model -> parser pattern."""

    def __init__(
        self,
        prompt_template: str,
        parser: BaseOutputParser,
        *,
        settings: Optional[RiskGPTSettings] = None,
        prompt_name: str = "",
    ) -> None:
        self.settings = settings or RiskGPTSettings()
        self.prompt_name = prompt_name
        self.parser = parser

        self.prompt = ChatPromptTemplate.from_template(
            template=prompt_template,
            partial_variables=self._partial_variables(),
        )

        if self.settings.OPENAI_API_KEY:
            self.model = ChatOpenAI(
                api_key=self.settings.OPENAI_API_KEY,
                temperature=self.settings.TEMPERATURE,
                model=self.settings.OPENAI_MODEL_NAME,
            )
        else:
            if hasattr(self.parser, "pydantic_object"):
                data: Dict[str, Any] = {}
                for name, field in self.parser.pydantic_object.model_fields.items():
                    ann = getattr(field.annotation, "__origin__", field.annotation)
                    if ann is list:
                        data[name] = []
                    elif ann in (int, float):
                        data[name] = 0
                    else:
                        data[name] = None
                dummy = self.parser.pydantic_object.model_construct(**data)
                self.model = FakeListLLM(responses=[dummy.model_dump_json()])
            else:
                self.model = FakeListLLM(responses=["{}"])

        self.memory = get_memory(self.settings)
        self.chain = self.prompt | self.model | self.parser

    def _partial_variables(self) -> Dict[str, str]:
        fmt = self.parser.get_format_instructions()
        fmt = fmt.replace("{", "{{").replace("}", "}}")
        return {"format_instructions": fmt}

    def invoke(self, inputs: Dict[str, Any]):
        with get_openai_callback() as cb:
            result = self.chain.invoke(inputs, memory=self.memory)
            if hasattr(result, "response_info"):
                result.response_info = ResponseInfo(
                    consumed_tokens=cb.total_tokens,
                    total_cost=cb.total_cost,
                    prompt_name=self.prompt_name,
                    model_name=self.settings.OPENAI_MODEL_NAME,
                )
            logger.info(
                "Consumed %s tokens (%.4f USD) for '%s' using %s",
                cb.total_tokens,
                cb.total_cost,
                self.prompt_name or "prompt",
                self.settings.OPENAI_MODEL_NAME,
            )
        return result

    async def invoke_async(self, inputs: Dict[str, Any]):
        """Asynchronously invoke the underlying chain."""
        with get_openai_callback() as cb:
            result = await self.chain.ainvoke(inputs, memory=self.memory)
            if hasattr(result, "response_info"):
                result.response_info = ResponseInfo(
                    consumed_tokens=cb.total_tokens,
                    total_cost=cb.total_cost,
                    prompt_name=self.prompt_name,
                    model_name=self.settings.OPENAI_MODEL_NAME,
                )
            logger.info(
                "Consumed %s tokens (%.4f USD) for '%s' using %s",
                cb.total_tokens,
                cb.total_cost,
                self.prompt_name or "prompt",
                self.settings.OPENAI_MODEL_NAME,
            )
        return result
