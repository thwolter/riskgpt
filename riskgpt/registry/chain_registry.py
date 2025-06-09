"""Registry for chain callables with utilities for external integration.

This module provides a registry for managing and accessing chains by name,
with additional utilities for introspection and server integration.

Example usage in external server frameworks:

```python
from fastapi import FastAPI
from pydantic import BaseModel
from riskgpt.registry import chain_registry

app = FastAPI()

@app.get("/chains")
def list_chains():
    return {"chains": chain_registry.get_chain_info()}

@app.post("/chain/{chain_name}")
def run_chain(chain_name: str, data: dict):
    if not chain_registry.chain_exists(chain_name):
        return {"error": f"Chain '{chain_name}' not found"}, 404
    chain_func = chain_registry.get(chain_name)
    return chain_func(**data)
```
"""

import inspect
from typing import Any, Callable, Dict, List, Optional, get_type_hints

_CHAIN_REGISTRY: Dict[str, Callable] = {}


def register(name: str) -> Callable[[Callable], Callable]:
    """Register a chain callable under the given name."""

    def decorator(func: Callable) -> Callable:
        _CHAIN_REGISTRY[name] = func
        return func

    return decorator


def get(name: str) -> Callable:
    """Retrieve a registered chain by name."""
    if name not in _CHAIN_REGISTRY:
        raise ValueError(f"Chain '{name}' is not registered")
    return _CHAIN_REGISTRY[name]


def available() -> List[str]:
    """Return a sorted list of available chain names."""
    return sorted(_CHAIN_REGISTRY)


def chain_exists(name: str) -> bool:
    """Check if a chain with the given name exists in the registry.

    Args:
        name: The name of the chain to check

    Returns:
        True if the chain exists, False otherwise
    """
    return name in _CHAIN_REGISTRY


def get_chain_info() -> List[Dict[str, Any]]:
    """Get detailed information about all registered chains.

    Returns:
        A list of dictionaries containing metadata for each chain:
        - name: The registered name of the chain
        - doc: The docstring of the chain function
        - input_type: The expected input type (if annotated)
        - output_type: The return type (if annotated)
    """
    result = []
    for name, func in sorted(_CHAIN_REGISTRY.items()):
        # Get type annotations if available
        type_hints = get_type_hints(func)

        # Extract input parameter type (usually first parameter)
        input_type = None
        signature = inspect.signature(func)
        if signature.parameters:
            first_param = next(iter(signature.parameters.values()))
            if (
                first_param.name != "self"
                and first_param.annotation != inspect.Parameter.empty
            ):
                input_type = str(first_param.annotation)

        # Get return type if annotated
        output_type = str(type_hints.get("return", "")) if type_hints else ""

        chain_info = {
            "name": name,
            "doc": inspect.getdoc(func) or "",
            "input_type": input_type,
            "output_type": output_type,
        }
        result.append(chain_info)

    return result


def get_chain_signature(name: str) -> Optional[Dict[str, Any]]:
    """Get detailed signature information for a specific chain.

    Args:
        name: The name of the registered chain

    Returns:
        A dictionary with detailed signature information or None if chain doesn't exist
    """
    if not chain_exists(name):
        return None

    func = get(name)
    signature = inspect.signature(func)

    params = []
    for param_name, param in signature.parameters.items():
        if param_name == "self":
            continue

        param_info = {
            "name": param_name,
            "required": param.default == inspect.Parameter.empty,
            "type": (
                str(param.annotation)
                if param.annotation != inspect.Parameter.empty
                else None
            ),
            "default": (
                None if param.default == inspect.Parameter.empty else param.default
            ),
        }
        params.append(param_info)

    return {
        "name": name,
        "doc": inspect.getdoc(func) or "",
        "parameters": params,
        "return_type": (
            str(signature.return_annotation)
            if signature.return_annotation != inspect.Signature.empty
            else None
        ),
    }
