import importlib

from riskgpt.registry.chain_registry import available, get

# Import chains package to trigger registration via decorators
importlib.import_module("riskgpt.chains")


def test_registry_contains_get_categories():
    assert "get_categories" in available()
    func = get("get_categories")
    assert callable(func)
