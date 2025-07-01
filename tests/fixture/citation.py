from datetime import date

import pytest
from pydantic import HttpUrl

from riskgpt.models.helpers.citation import Citation


@pytest.fixture
def minimal_citation():
    """Return a minimal citation with only URL."""
    return Citation(url=HttpUrl("https://example.com"))


@pytest.fixture
def partial_citation():
    """Return a partial citation with URL and title."""
    return Citation(
        url=HttpUrl("https://example.com"),
        title="Example Title",
    )


@pytest.fixture
def complete_citation():
    """Return a complete citation with all fields populated."""
    return Citation(
        url=HttpUrl("https://example.com"),
        title="Example Title",
        authors=["John Doe"],
        publication_date=date(2023, 1, 1),
        venue="Example Venue",
        publisher="Example Publisher",
    )
