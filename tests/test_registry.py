import importlib
import sys

from riskgpt.registry.chain_registry import available, get

# Force reload of the chains module to ensure decorators are applied
if "riskgpt.chains" in sys.modules:
    del sys.modules["riskgpt.chains"]

# Import chains package to trigger registration via decorators
importlib.import_module("riskgpt.chains")


def test_registry_contains_get_categories():
    assert "get_categories" in available()
    func = get("get_categories")
    assert callable(func)
