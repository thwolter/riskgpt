import logging
from unittest.mock import AsyncMock

import pytest
from langchain_community.callbacks import get_openai_callback
from langchain_core.output_parsers import BaseOutputParser

from src.riskgpt.chains.base import BaseChain
from src.riskgpt.logger import configure_logging
from src.riskgpt.models.base import ResponseInfo
from src.riskgpt.models.chains.categorization import CategoryResponse

logger = logging.getLogger("src")


class DummyParser(BaseOutputParser):
    def parse(self, text):
        return CategoryResponse(categories=["foo"], rationale=None)

    def get_format_instructions(self) -> str:
        return ""


@pytest.mark.asyncio
async def test_token_logging(monkeypatch, caplog):
    caplog.set_level(logging.INFO, logger="src")
    configure_logging(level=logging.INFO)

    # Create a mock chain with an ainvoke method
    mock_chain = AsyncMock()
    mock_response = CategoryResponse(categories=["foo"], rationale=None)
    mock_chain.ainvoke.return_value = mock_response

    # Create the DummyCB class for the OpenAI callback
    class DummyCB:
        def __enter__(self):
            self.total_tokens = 3
            self.total_cost = 0.001
            return self

        def __exit__(self, exc_type, exc, tb):
            pass

    # Create a simple function that logs token usage
    async def fake_invoke(inputs):
        with get_openai_callback() as cb:
            # Simulate calling the chain
            result = mock_response
            # Add response info
            if hasattr(result, "response_info"):
                result.response_info = ResponseInfo(
                    consumed_tokens=cb.total_tokens,
                    total_cost=cb.total_cost,
                    prompt_name="test",
                    model_name="test-model",
                )
            # Log the token usage
            logger.info(
                "Consumed %s tokens (%.4f USD) for '%s' using %s",
                cb.total_tokens,
                cb.total_cost,
                "test",
                "test-model",
            )
            return result

    # Mock the get_openai_callback function
    monkeypatch.setattr(
        "langchain_community.callbacks.get_openai_callback", lambda: DummyCB()
    )

    # Create a BaseChain instance and replace its invoke method
    parser = DummyParser()
    chain = BaseChain(prompt_template="hi", parser=parser)
    monkeypatch.setattr(chain, "invoke", fake_invoke)

    # Call the method and await it
    await chain.invoke({})

    # Check that the log message was generated
    assert any("Consumed" in record.getMessage() for record in caplog.records)
