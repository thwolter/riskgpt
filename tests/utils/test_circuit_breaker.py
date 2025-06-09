"""Tests for the circuit breaker module."""

import os

import pytest

from riskgpt.utils.circuit_breaker import (
    PYBREAKER_AVAILABLE,
    duckduckgo_breaker,
    openai_breaker,
    with_fallback,
)


def test_circuit_breaker_imports():
    """Test that the circuit breaker module imports correctly."""
    assert duckduckgo_breaker is not None
    assert openai_breaker is not None
    assert with_fallback is not None


def test_with_fallback_decorator():
    """Test that the with_fallback decorator works correctly."""

    # Define a function that will fail
    def failing_function():
        raise Exception("This function always fails")

    # Define a fallback function
    def fallback_function():
        return "Fallback response"

    # Apply the decorator
    decorated_function = with_fallback(fallback_function)(failing_function)

    # Call the decorated function
    result = decorated_function()

    # Check that the fallback was used
    assert result == "Fallback response"


@pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set"
)
def test_circuit_breaker_decorator():
    """Test that the circuit breaker decorator works correctly."""
    # This is a basic test that just ensures the decorator doesn't crash
    # A more comprehensive test would require mocking the pybreaker library

    @openai_breaker
    def sample_function():
        return "Success"

    result = sample_function()
    assert result == "Success"


@pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set"
)
def test_fallback_with_circuit_breaker():
    """Test that the fallback works with the circuit breaker."""
    # Skip if pybreaker is not available
    if not PYBREAKER_AVAILABLE:
        pytest.skip("pybreaker not available")

    # Define a function that will fail
    @openai_breaker
    @with_fallback(lambda: "Fallback response")
    def failing_function():
        raise Exception("This function always fails")

    # Call the decorated function
    result = failing_function()

    # Check that the fallback was used
    assert result == "Fallback response"
