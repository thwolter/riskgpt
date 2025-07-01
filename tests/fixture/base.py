import logging
import os
from unittest.mock import AsyncMock

import pytest

from riskgpt.logger import configure_logging
from riskgpt.models.base import ResponseInfo


# Automatically apply skip_if_no_openai_key to integration tests
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "integration: tests requiring real external services"
    )


def pytest_collection_modifyitems(items):
    for item in items:
        if "integration" in item.keywords:
            item.fixturenames.append("skip_if_no_openai_key")


@pytest.fixture(autouse=True)
def set_max_tokens_for_tests(monkeypatch):
    """Set MAX_TOKENS to a small value for all tests."""
    # Set the MAX_TOKENS environment variable for tests
    # Using 400 instead of 10 to ensure the model can generate a valid response
    # with all required fields for all risks while still limiting token usage
    monkeypatch.setenv("MAX_TOKENS", "5000")


@pytest.fixture(autouse=True)
def skip_if_no_openai_key(request):
    if "integration" in request.keywords and not os.environ.get("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set")


@pytest.fixture
def configure_test_logging(caplog):
    """Configure logging for tests."""
    caplog.set_level(logging.INFO, logger="riskgpt")
    configure_logging(level=logging.INFO)
    return caplog


@pytest.fixture
def sample_response_info():
    """Return a ResponseInfo object with mock data."""

    def factory(prompt_name="sample-prompt", error=None):
        """Factory function to create ResponseInfo with a specific prompt name."""
        response_info = ResponseInfo(
            consumed_tokens=100,
            total_cost=0.002,
            prompt_name=prompt_name,
            model_name="gpt-4",
        )
        if error:
            response_info.error = error
        return response_info

    return factory


@pytest.fixture
def mock_chain():
    """Return a mock chain that can be configured with different responses."""
    mock = AsyncMock()
    mock.invoke = AsyncMock()
    return mock
