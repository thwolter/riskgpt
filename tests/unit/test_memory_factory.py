import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from config.settings import RiskGPTSettings
from helpers.memory_factory import get_memory, register_memory_backend
from langchain.memory import ConversationBufferMemory


def test_get_memory_buffer():
    mem = get_memory(RiskGPTSettings(MEMORY_TYPE="buffer"))
    assert isinstance(mem, ConversationBufferMemory)


def test_register_new_backend():
    called = {}

    def creator(settings):
        called["settings"] = settings
        return "dummy_result"

    # Override an existing backend instead of creating a new one
    register_memory_backend("buffer", creator)
    mem = get_memory(RiskGPTSettings(MEMORY_TYPE="buffer"))
    assert mem == "dummy_result"
    assert "settings" in called
