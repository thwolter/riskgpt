import importlib
import sys

from src.registry.chain_registry import available, get


def _reload_chains():
    """Reload chain modules so decorators register functions."""
    if "src.chains" in sys.modules:
        del sys.modules["src.chains"]
        for mod in [m for m in list(sys.modules) if m.startswith("src.chains.")]:
            del sys.modules[mod]
    importlib.import_module("src.chains")


def test_registry_contains_get_categories():
    _reload_chains()
    assert "get_categories" in available()
    func = get("get_categories")
    assert callable(func)
