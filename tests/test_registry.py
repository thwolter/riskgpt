import importlib
import sys

from riskgpt.registry.chain_registry import available, get


def _reload_chains():
    """Reload chain modules so decorators register functions."""
    if "riskgpt.chains" in sys.modules:
        del sys.modules["riskgpt.chains"]
        for mod in [m for m in list(sys.modules) if m.startswith("riskgpt.chains.")]:
            del sys.modules[mod]
    importlib.import_module("riskgpt.chains")


def test_registry_contains_get_categories():
    _reload_chains()
    assert "get_categories" in available()
    func = get("get_categories")
    assert callable(func)
