import logging
from types import SimpleNamespace

import pytest

pytest.importorskip("langchain")
pytest.importorskip("langchain_openai")
pytest.importorskip("langchain_community")

from langchain_core.output_parsers import BaseOutputParser

from riskgpt.chains.base import BaseChain
from riskgpt.logger import configure_logging
from riskgpt.models.schemas import CategoryResponse


class DummyParser(BaseOutputParser):
    def parse(self, text):
        return CategoryResponse(categories=["foo"], rationale=None)

    def get_format_instructions(self) -> str:
        return ""


def test_token_logging(monkeypatch, caplog):
    caplog.set_level(logging.INFO, logger="riskgpt")
    configure_logging(level=logging.INFO)

    parser = DummyParser()
    chain = BaseChain(prompt_template="hi", parser=parser)

    def fake_invoke(inputs, memory=None):
        return CategoryResponse(categories=["foo"], rationale=None)

    class DummyCB:
        def __enter__(self):
            self.total_tokens = 3
            self.total_cost = 0.001
            return self

        def __exit__(self, exc_type, exc, tb):
            pass

    monkeypatch.setattr(chain, "chain", SimpleNamespace(invoke=fake_invoke))
    monkeypatch.setattr("riskgpt.chains.base.get_openai_callback", lambda: DummyCB())

    chain.invoke({})

    assert any("Consumed" in record.getMessage() for record in caplog.records)
