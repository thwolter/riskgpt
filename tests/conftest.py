# ruff: noqa: F401

import sys
from pathlib import Path

from dotenv import load_dotenv

from tests.fixture.base import (
    configure_test_logging,
    mock_chain,
    pytest_collection_modifyitems,
    pytest_configure,
    sample_response_info,
    set_max_tokens_for_tests,
    skip_if_no_openai_key,
)
from tests.fixture.citation import (
    complete_citation,
    minimal_citation,
    partial_citation,
)
from tests.fixture.keypoint import (
    academic_keypoint,
    mock_academic_keypoints_response,
    mock_keypoints_response,
    mock_news_keypoints_response,
    news_keypoint,
)
from tests.fixture.research import (
    keypoint_text_resp,
    mock_extract_key_points,
    mock_key_points,
    mock_keypoints_summary_chain,
    state_with_sources,
    test_request,
)
from tests.fixture.source import (
    academic_source,
    news_source,
)

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# Load environment variables from .env file
dotenv_path = ROOT / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path=dotenv_path)
