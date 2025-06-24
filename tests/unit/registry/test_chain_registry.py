from typing import Any, Dict, List

import pytest

from src.registry.chain_registry import (
    available,
    chain_exists,
    get,
    get_chain_info,
    get_chain_signature,
    register,
)


# Test fixtures
@pytest.fixture
def setup_test_registry():
    # Clean up registry between tests
    from src.registry.chain_registry import _CHAIN_REGISTRY

    _CHAIN_REGISTRY.clear()

    # Register test functions
    @register("test_func")
    def test_function(param1: str, param2: int = 42) -> str:
        """Test function docstring."""
        return f"{param1}: {param2}"

    @register("another_func")
    def another_function(data: Dict[str, Any]) -> List[str]:
        """Another test function."""
        return list(data.keys())

    yield

    # Clean up after tests
    _CHAIN_REGISTRY.clear()


# Test basic registry functionality
def test_register_and_get(setup_test_registry):
    # Test retrieval of registered function
    func = get("test_func")
    assert func("hello") == "hello: 42"

    # Test function with different signature
    another = get("another_func")
    assert another({"a": 1, "b": 2}) == ["a", "b"]

    # Test error on non-existent function
    with pytest.raises(ValueError):
        get("non_existent")


def test_available(setup_test_registry):
    # Test listing available chains
    chains = available()
    assert "test_func" in chains
    assert "another_func" in chains
    assert len(chains) == 2


def test_chain_exists(setup_test_registry):
    # Test chain existence check
    assert chain_exists("test_func")
    assert chain_exists("another_func")
    assert not chain_exists("non_existent")


# Test enhanced functionality
def test_get_chain_info(setup_test_registry):
    # Test chain info retrieval
    info = get_chain_info()
    assert len(info) == 2

    # Find test_func info
    test_func_info = next(i for i in info if i["name"] == "test_func")
    assert "Test function docstring" in test_func_info["doc"]
    assert "str" in test_func_info["input_type"]
    assert "str" in test_func_info["output_type"]

    # Find another_func info
    another_func_info = next(i for i in info if i["name"] == "another_func")
    assert "Another test function" in another_func_info["doc"]
    assert "Dict" in another_func_info["input_type"]
    assert "List" in another_func_info["output_type"]


def test_get_chain_signature(setup_test_registry):
    # Test signature for specific chain
    signature = get_chain_signature("test_func")
    assert signature["name"] == "test_func"
    assert "Test function docstring" in signature["doc"]

    # Check parameters
    params = signature["parameters"]
    assert len(params) == 2

    # Check param1
    param1 = next(p for p in params if p["name"] == "param1")
    assert param1["required"] is True
    assert "str" in param1["type"]

    # Check param2
    param2 = next(p for p in params if p["name"] == "param2")
    assert param2["required"] is False
    assert "int" in param2["type"]
    assert param2["default"] == 42

    # Test non-existent chain
    assert get_chain_signature("non_existent") is None
