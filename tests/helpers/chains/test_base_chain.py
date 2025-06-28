"""
test_base_chain.py

This module contains asynchronous unit tests for the `BaseChain` class from the `src.chains.base` module.
The tests focus on verifying correct invocation logic, output parsing, and logging behaviors within an async context.

Key Components:
---------------
- DummyParser:
    A stub implementation of `BaseOutputParser` that returns a static category response for testing purposes.

- test_invoke:
    An asynchronous test function that:
    - Sets up logging capture and initializes a test logger.
    - Configures a `BaseChain` instance using a dummy prompt template and parser.
    - Replaces the real chain invocation and callback logic with dummy implementations using `monkeypatch`.
    - Triggers the `BaseChain.invoke()` method to ensure output parsing and logging of resource consumption is handled properly.
    - Verifies that a consumption-related log entry is produced.

Test Utilities:
---------------
- `monkeypatch`: Used to inject test implementations for asynchronous invocation and callback mechanisms.
- `caplog`: Utilized to capture and assert log records during test execution.

Dependencies:
-------------
- pytest (with asyncio support)
- langchain_core.output_parsers
- src.chains.base.BaseChain
- src.logger.configure_logging
- src.models.chains.categorization.CategoryResponse

Purpose:
--------
These tests are designed to ensure that asynchronous invocation and result parsing by `BaseChain` work correctly,
tokens and cost logging is triggered as expected, and the integration between chain, parser, and logging functions is robust under controlled conditions.
"""

import logging
from types import SimpleNamespace

import pytest
from langchain_core.exceptions import OutputParserException
from langchain_core.output_parsers import BaseOutputParser
from langchain_core.output_parsers.pydantic import PydanticOutputParser
from riskgpt.chains.base import BaseChain
from riskgpt.logger import configure_logging
from riskgpt.models.chains.categorization import CategoryResponse


class DummyParser(BaseOutputParser):
    def parse(self, text):
        return CategoryResponse(categories=["foo"], rationale=None)

    def get_format_instructions(self) -> str:
        return ""


@pytest.mark.asyncio
async def test_invoke(monkeypatch, caplog):
    caplog.set_level(logging.INFO, logger="src")
    configure_logging(level=logging.INFO)

    parser = DummyParser()
    chain = BaseChain(prompt_template="hi", parser=parser)

    async def fake_ainvoke(inputs, memory=None):
        return CategoryResponse(categories=["foo"], rationale=None)

    class DummyCB:
        def __enter__(self):
            self.total_tokens = 3
            self.total_cost = 0.001
            return self

        def __exit__(self, exc_type, exc, tb):
            pass

    monkeypatch.setattr(chain, "chain", SimpleNamespace(ainvoke=fake_ainvoke))
    monkeypatch.setattr(
        "langchain_community.callbacks.get_openai_callback", lambda: DummyCB()
    )

    await chain.invoke({})

    assert any("Consumed" in record.getMessage() for record in caplog.records)


@pytest.mark.asyncio
async def test_invoke_with_parser_exception(monkeypatch, caplog):
    """Test that OutputParserException is handled correctly."""
    caplog.set_level(logging.ERROR, logger="src")
    configure_logging(level=logging.ERROR)

    # Use PydanticOutputParser instead of DummyParser
    parser = PydanticOutputParser(pydantic_object=CategoryResponse)
    chain = BaseChain(prompt_template="hi", parser=parser)

    async def fake_ainvoke_with_error(inputs, memory=None):
        raise OutputParserException("Failed to parse output", llm_output="Invalid JSON")

    class DummyCB:
        def __enter__(self):
            self.total_tokens = 3
            self.total_cost = 0.001
            return self

        def __exit__(self, exc_type, exc, tb):
            pass

    monkeypatch.setattr(
        chain, "chain", SimpleNamespace(ainvoke=fake_ainvoke_with_error)
    )
    monkeypatch.setattr(
        "langchain_community.callbacks.get_openai_callback", lambda: DummyCB()
    )

    result = await chain.invoke({})

    # Verify that the error was logged
    assert any(
        "Output parser error" in record.getMessage() for record in caplog.records
    )

    # Verify that a fallback response was created
    assert isinstance(result, CategoryResponse)

    # Verify that the response_info contains the error
    assert result.response_info is not None
    assert "Output parser error" in result.response_info.error
