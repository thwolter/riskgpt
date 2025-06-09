from __future__ import annotations

import typing
from typing import Any, Dict, Optional

from langchain_community.callbacks import get_openai_callback
from langchain_community.llms import FakeListLLM
from langchain_core.output_parsers import BaseOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from riskgpt.config.settings import RiskGPTSettings
from riskgpt.logger import logger
from riskgpt.models.schemas import ResponseInfo
from riskgpt.utils.circuit_breaker import openai_breaker, with_fallback
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
                    ann = field.annotation
                    origin = typing.get_origin(ann) or ann
                    args = typing.get_args(ann)
                    if origin is list or any(
                        typing.get_origin(a) is list for a in args
                    ):
                        item = args[0] if args else str
                        item_origin = typing.get_origin(item) or item
                        if isinstance(item_origin, type) and issubclass(
                            item_origin, BaseModel
                        ):
                            item_cls = typing.cast(type[BaseModel], item_origin)
                            item_data: Dict[str, Any] = {}
                            for f_name, f in item_cls.model_fields.items():
                                f_origin = (
                                    typing.get_origin(f.annotation) or f.annotation
                                )
                                if f_origin is str:
                                    item_data[f_name] = "dummy"
                                elif f_origin in {int, float}:
                                    item_data[f_name] = 0
                                else:
                                    item_data[f_name] = None
                            item_instance = item_cls.model_validate(item_data)
                            data[name] = [item_instance]
                        elif item_origin is str:
                            data[name] = ["dummy"]
                        else:
                            data[name] = []
                    elif str in {origin, *args}:
                        data[name] = "dummy"
                    elif int in {origin, *args}:
                        data[name] = 0
                    elif float in {origin, *args}:
                        data[name] = 0.0
                    else:
                        data[name] = None
                dummy = self.parser.pydantic_object.model_validate(data)
                self.model = FakeListLLM(responses=[dummy.model_dump_json()])
            else:
                self.model = FakeListLLM(responses=["{}"])

        self.memory = get_memory(self.settings)
        self.chain = self.prompt | self.model | self.parser

    def _partial_variables(self) -> Dict[str, str]:
        fmt = self.parser.get_format_instructions()
        fmt = fmt.replace("{", "{{").replace("}", "}}")
        return {"format_instructions": fmt}

    def _fallback_response(self, inputs: Dict[str, Any]):
        """Fallback response when the circuit is open."""
        logger.warning(
            "Circuit is open for OpenAI API, using fallback response for '%s'",
            self.prompt_name or "prompt",
        )

        # If we have a parser with a pydantic object, create a minimal valid response
        if hasattr(self.parser, "pydantic_object"):
            try:
                # Create a minimal valid instance of the pydantic object
                data: Dict[str, Any] = {}
                for name, field in self.parser.pydantic_object.model_fields.items():
                    if field.is_required():
                        if field.annotation is str or typing.get_origin(field.annotation) is str:
                            data[name] = "Service temporarily unavailable"
                        elif field.annotation is list or typing.get_origin(field.annotation) is list:
                            data[name] = []
                        else:
                            data[name] = None

                result = self.parser.pydantic_object.model_validate(data)

                # Add response info if supported
                if hasattr(result, "response_info"):
                    result.response_info = ResponseInfo(
                        consumed_tokens=0,
                        total_cost=0.0,
                        prompt_name=self.prompt_name,
                        model_name=self.settings.OPENAI_MODEL_NAME,
                        error="Service temporarily unavailable",
                    )
                return result
            except Exception as e:
                logger.error("Failed to create fallback response: %s", e)

        # If we can't create a valid pydantic object, return a simple dict
        return {"error": "Service temporarily unavailable"}

    @openai_breaker
    @with_fallback(_fallback_response)
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

    async def _async_fallback_response(self, inputs: Dict[str, Any]):
        """Async fallback response when the circuit is open."""
        # Reuse the same logic as the sync fallback
        return self._fallback_response(inputs)

    @openai_breaker
    @with_fallback(_async_fallback_response)
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
