import os
import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Load environment variables from .env file
dotenv_path = ROOT / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path=dotenv_path)


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
