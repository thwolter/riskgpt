"""Simple registry for chain callables."""

from typing import Callable, Dict, List

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
