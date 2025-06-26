# riskgpt/__init__.py
"""
Public helpers already here …
"""

import sys
from importlib import import_module

# ----------------------------------------------------------------------
# Expose top-level packages as sub-packages under `riskgpt.*`
# (avoids refactoring dozens of existing import statements)
# ----------------------------------------------------------------------
for _name in (
    "models",
    "workflows",
    "chains",
    "utils",
    "processors",
    "config",
    "prompts",
):
    try:
        _mod = import_module(_name)  # import the existing top-level package
        sys.modules[f"{__name__}.{_name}"] = _mod  # alias it as riskgpt.<name>
    except ModuleNotFoundError:
        # Package not present – ignore silently
        pass
del import_module, sys, _name, _mod
