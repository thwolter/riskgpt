import pytest

from riskgpt.models.enums import ScopeEnum
from riskgpt.models.helpers.search import Source


@pytest.fixture
def news_source(complete_citation):
    """Return a news source with complete citation."""
    return Source(
        content="This is a test news article about technology and finance.",
        scope=ScopeEnum.NEWS,
        citation=complete_citation,
    )


@pytest.fixture
def academic_source(complete_citation):
    """Return an academic source with complete citation."""
    return Source(
        content="This is a test academic paper with important findings.",
        scope=ScopeEnum.ACADEMIC,
        citation=complete_citation,
    )
