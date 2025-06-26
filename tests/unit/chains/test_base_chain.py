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
from langchain_core.output_parsers import BaseOutputParser

from src import BaseChain
from src import configure_logging
from src import CategoryResponse


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
