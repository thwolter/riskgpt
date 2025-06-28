from datetime import date

from riskgpt.models.helpers.citation import Citation


class TestCitation:
    def test_format_harvard_citation_with_one_author(self):
        citation = Citation(
            url="https://example.com",
            title="Example Title",
            authors=["John Doe"],
            publication_date=date(2023, 1, 1),
            venue="Example Venue",
        )

        result = citation.format_harvard_citation()
        assert result == "John Doe (2023)"

    def test_format_harvard_citation_with_two_authors(self):
        citation = Citation(
            url="https://example.com",
            title="Example Title",
            authors=["John Doe", "Jane Smith"],
            publication_date=date(2023, 1, 1),
            venue="Example Venue",
        )

        result = citation.format_harvard_citation()
        assert result == "John Doe and Jane Smith (2023)"

    def test_format_harvard_citation_with_multiple_authors(self):
        citation = Citation(
            url="https://example.com",
            title="Example Title",
            authors=["John Doe", "Jane Smith", "Bob Johnson"],
            publication_date=date(2023, 1, 1),
            venue="Example Venue",
        )

        result = citation.format_harvard_citation()
        assert result == "John Doe et al. (2023)"

    def test_format_harvard_citation_without_authors(self):
        citation = Citation(
            url="https://example.com",
            title="Example Title",
            authors=[],
            publication_date=date(2023, 1, 1),
            venue="Example Venue",
        )

        result = citation.format_harvard_citation()
        assert result == "example.com (2023)"

    def test_format_harvard_citation_without_date(self):
        citation = Citation(
            url="https://example.com",
            title="Example Title",
            authors=["John Doe"],
            publication_date=None,
            venue="Example Venue",
        )

        result = citation.format_harvard_citation()
        assert result == "John Doe"

    def test_format_harvard_reference_with_one_author(self):
        citation = Citation(
            url="https://example.com",
            title="Example Title",
            authors=["John Doe"],
            publication_date=date(2023, 1, 1),
            venue="Example Venue",
        )

        result = citation.format_harvard_reference()
        # We can't test the exact string because it includes the current date
        assert "John Doe (2023). Example Title. Example Venue." in result
        assert "Available at: https://example.com" in result

    def test_format_harvard_reference_with_multiple_authors(self):
        citation = Citation(
            url="https://example.com",
            title="Example Title",
            authors=["John Doe", "Jane Smith", "Bob Johnson"],
            publication_date=date(2023, 1, 1),
            venue="Example Venue",
        )

        result = citation.format_harvard_reference()
        # We can't test the exact string because it includes the current date
        assert (
            "John Doe, Jane Smith and Bob Johnson (2023). Example Title. Example Venue."
            in result
        )
        assert "Available at: https://example.com" in result

    def test_format_harvard_reference_with_many_authors(self):
        citation = Citation(
            url="https://example.com",
            title="Example Title",
            authors=["John Doe", "Jane Smith", "Bob Johnson", "Alice Brown"],
            publication_date=date(2023, 1, 1),
            venue="Example Venue",
        )

        result = citation.format_harvard_reference()
        # We can't test the exact string because it includes the current date
        assert "John Doe et al. (2023). Example Title. Example Venue." in result
        assert "Available at: https://example.com" in result

    def test_format_harvard_reference_without_authors(self):
        citation = Citation(
            url="https://example.com",
            title="Example Title",
            authors=[],
            publication_date=date(2023, 1, 1),
            venue="Example Venue",
        )

        result = citation.format_harvard_reference()
        # We can't test the exact string because it includes the current date
        assert "example.com (2023). Example Title. Example Venue." in result
        assert "Available at: https://example.com" in result

    def test_format_harvard_reference_without_title(self):
        citation = Citation(
            url="https://example.com",
            title=None,
            authors=["John Doe"],
            publication_date=date(2023, 1, 1),
            venue="Example Venue",
        )

        result = citation.format_harvard_reference()
        # We can't test the exact string because it includes the current date
        assert "John Doe (2023). Untitled. Example Venue." in result
        assert "Available at: https://example.com" in result

    def test_format_harvard_reference_without_venue(self):
        citation = Citation(
            url="https://example.com",
            title="Example Title",
            authors=["John Doe"],
            publication_date=date(2023, 1, 1),
            venue=None,
        )

        result = citation.format_harvard_reference()
        # We can't test the exact string because it includes the current date
        assert "John Doe (2023). Example Title." in result
        assert "Available at: https://example.com" in result
