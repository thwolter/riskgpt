import logging
from types import SimpleNamespace

import pytest
from langchain_core.output_parsers import BaseOutputParser

from riskgpt.chains.base import BaseChain
from riskgpt.logger import configure_logging
from riskgpt.models.schemas import CategoryResponse


class DummyParser(BaseOutputParser):
    def parse(self, text):
        return CategoryResponse(categories=["foo"], rationale=None)

    def get_format_instructions(self) -> str:
        return ""


@pytest.mark.asyncio
async def test_invoke(monkeypatch, caplog):
    caplog.set_level(logging.INFO, logger="riskgpt")
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
