from datetime import date

import pytest
from pydantic import HttpUrl

from riskgpt.models.chains.keypoints import KeyPoint
from riskgpt.models.enums import ScopeEnum
from riskgpt.models.helpers.citation import Citation


class TestCitationFormatting:
    """
    Tests for citation formatting in KeyPoint model.

    This class tests how citations are formatted in different scenarios,
    including complete citations, partial citations, and edge cases.
    """

    @pytest.mark.parametrize(
        "citation_data,expected_output",
        [
            # Complete citation with single author
            (
                {
                    "url": "https://example.com",
                    "title": "Example Title",
                    "authors": ["John Doe"],
                    "publication_date": date(2023, 1, 1),
                    "venue": "Example Venue",
                },
                "John Doe (2023)",
            ),
            # Complete citation with two authors
            (
                {
                    "url": "https://example.com",
                    "title": "Example Title",
                    "authors": ["John Doe", "Jane Smith"],
                    "publication_date": date(2023, 1, 1),
                    "venue": "Example Venue",
                },
                "John Doe and Jane Smith (2023)",
            ),
            # Complete citation with three authors
            (
                {
                    "url": "https://example.com",
                    "title": "Example Title",
                    "authors": ["John Doe", "Jane Smith", "Bob Johnson"],
                    "publication_date": date(2023, 1, 1),
                    "venue": "Example Venue",
                },
                "John Doe et al. (2023)",
            ),
            # Minimal citation (URL only)
            (
                {"url": "https://example.com"},
                "example.com",
            ),
            # Citation with URL and title but no authors
            (
                {
                    "url": "https://example.com",
                    "title": "Example Title",
                },
                "example.com",
            ),
            # Citation with URL and authors but no date
            (
                {
                    "url": "https://example.com",
                    "title": "Example Title",
                    "authors": ["John Doe"],
                },
                "John Doe",
            ),
        ],
    )
    def test_get_inline_citation(self, citation_data, expected_output):
        """Test citation formatting with various citation data combinations."""
        # Create Citation object from the test data
        citation = Citation(url=HttpUrl(citation_data["url"]))

        # Add optional fields if present in the test data
        if "title" in citation_data:
            citation.title = citation_data["title"]
        if "authors" in citation_data:
            citation.authors = citation_data["authors"]
        if "publication_date" in citation_data:
            citation.publication_date = citation_data["publication_date"]
        if "venue" in citation_data:
            citation.venue = citation_data["venue"]
        if "publisher" in citation_data:
            citation.publisher = citation_data["publisher"]

        # Create KeyPoint with the citation
        keypoint = KeyPoint(
            content="This is a key point",
            scope=ScopeEnum.NEWS,
            citation=citation,
        )

        # Test the inline citation formatting
        result = keypoint.get_inline_citation()
        assert result == expected_output

    def test_citation_completeness(
        self, complete_citation, partial_citation, minimal_citation
    ):
        """Test the is_complete method of Citation."""
        assert complete_citation.is_complete() is True
        assert partial_citation.is_complete() is False
        assert minimal_citation.is_complete() is False

    def test_citation_equality(self, complete_citation):
        """Test the equality comparison of Citation objects."""
        # Same citation should be equal
        citation_copy = Citation(
            url=HttpUrl("https://example.com"),
            title="Example Title",
            authors=["John Doe"],
            publication_date=date(2023, 1, 1),
            venue="Example Venue",
            publisher="Example Publisher",
        )
        assert complete_citation == citation_copy

        # Different URL should not be equal
        different_url = Citation(
            url=HttpUrl("https://different.com"),
            title="Example Title",
            authors=["John Doe"],
            publication_date=date(2023, 1, 1),
            venue="Example Venue",
            publisher="Example Publisher",
        )
        assert complete_citation != different_url

        # String comparison with URL
        assert complete_citation == "https://example.com"
        assert complete_citation != "https://different.com"

    def test_harvard_reference_formatting(self, complete_citation):
        """Test the format_harvard_reference method of Citation."""
        reference = complete_citation.format_harvard_reference()

        # Check that the reference contains the expected components
        assert "John Doe" in reference
        assert "(2023)" in reference
        assert "Example Title" in reference
        assert "Example Venue" in reference
        assert "https://example.com" in reference
        assert "[Accessed:" in reference

    @pytest.mark.parametrize(
        "authors,expected_start",
        [
            (["John Doe"], "John Doe"),
            (["John Doe", "Jane Smith"], "John Doe and Jane Smith"),
            (
                ["John Doe", "Jane Smith", "Bob Johnson"],
                "John Doe, Jane Smith and Bob Johnson",
            ),
            (
                ["John Doe", "Jane Smith", "Bob Johnson", "Alice Brown"],
                "John Doe et al.",
            ),
            ([], "example.com"),
        ],
    )
    def test_harvard_reference_author_formatting(
        self, complete_citation, authors, expected_start
    ):
        """Test author formatting in Harvard references with different numbers of authors."""
        # Create a copy of the citation with the test authors
        citation = Citation(
            url=HttpUrl("https://example.com"),
            title=complete_citation.title,
            authors=authors,
            publication_date=complete_citation.publication_date,
            venue=complete_citation.venue,
            publisher=complete_citation.publisher,
        )

        reference = citation.format_harvard_reference()
        assert reference.startswith(expected_start)

    def test_edge_case_empty_fields(self):
        """Test citation formatting with empty fields."""
        # Citation with empty title
        citation = Citation(
            url=HttpUrl("https://example.com"),
            title="",
            authors=["John Doe"],
            publication_date=date(2023, 1, 1),
        )
        reference = citation.format_harvard_reference()
        assert "Untitled" in reference

        # Citation with empty authors list
        citation = Citation(
            url=HttpUrl("https://example.com"),
            title="Example Title",
            authors=[],
            publication_date=date(2023, 1, 1),
        )
        inline = citation.format_harvard_citation()
        assert inline == "example.com (2023)"
