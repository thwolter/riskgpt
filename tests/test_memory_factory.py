import pathlib
import sys
import pytest

pytest.importorskip("pydantic")
from pydantic import ValidationError

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
pytest.importorskip("langchain")

from riskgpt.utils.memory_factory import get_memory, register_memory_backend
from riskgpt.config.settings import RiskGPTSettings
from langchain.memory import ConversationBufferMemory


def test_get_memory_buffer():
    mem = get_memory(RiskGPTSettings(MEMORY_TYPE="buffer"))
    assert isinstance(mem, ConversationBufferMemory)


def test_get_memory_unknown():
    with pytest.raises(ValidationError) as exc_info:
        get_memory(RiskGPTSettings(MEMORY_TYPE="unknown"))
    assert "MEMORY_TYPE" in str(exc_info.value)
    assert "Input should be 'none', 'buffer' or 'redis'" in str(exc_info.value)


def test_register_new_backend():
    called = {}

    def creator(settings):
        called['settings'] = settings
        return "dummy"

    register_memory_backend("dummy", creator)
    mem = get_memory(RiskGPTSettings(MEMORY_TYPE="dummy"))
    assert mem == "dummy"
    assert 'settings' in called


