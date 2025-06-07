from types import SimpleNamespace
import asyncio
import logging
import pytest

pytest.importorskip("langchain")
pytest.importorskip("langchain_openai")
pytest.importorskip("langchain_community")

from riskgpt.logger import configure_logging
from riskgpt.chains.base import BaseChain
from langchain_core.output_parsers import BaseOutputParser
from riskgpt.models.schemas import CategoryResponse


class DummyParser(BaseOutputParser):
    def parse(self, text):
        return CategoryResponse(categories=["foo"], rationale=None)

    def get_format_instructions(self) -> str:
        return ""


def test_async_invoke(monkeypatch, caplog):
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
    monkeypatch.setattr("riskgpt.chains.base.get_openai_callback", lambda: DummyCB())

    asyncio.run(chain.invoke_async({}))

    assert any("Consumed" in record.getMessage() for record in caplog.records)

