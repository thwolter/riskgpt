import pathlib
import sys

import pytest
from pydantic import ValidationError

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from langchain.memory import ConversationBufferMemory

from src.config.settings import RiskGPTSettings
from src.utils.memory_factory import get_memory, register_memory_backend


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
        called["settings"] = settings
        return "dummy"

    register_memory_backend("dummy", creator)
    mem = get_memory(RiskGPTSettings(MEMORY_TYPE="dummy"))
    assert mem == "dummy"
    assert "settings" in called
