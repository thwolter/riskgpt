from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field


class Citation(BaseModel):
    """Structured citation information for a source."""

    url: str = Field(description="URL of the source")
    title: Optional[str] = Field(default=None, description="Title of the source")
    authors: List[str] = Field(default_factory=list, description="List of author names")
    publication_date: Optional[date] = Field(
        default=None, description="Publication date"
    )
    venue: Optional[str] = Field(
        default=None, description="Publication venue (journal, conference, etc.)"
    )
    publisher: Optional[str] = Field(default=None, description="Publisher name")

    def format_harvard_citation(self) -> str:
        """Format the citation in Harvard style."""
        # Author formatting
        author_text = ""
        if self.authors:
            if len(self.authors) == 1:
                author_text = self.authors[0]
            elif len(self.authors) == 2:
                author_text = f"{self.authors[0]} and {self.authors[1]}"
            elif len(self.authors) > 2:
                author_text = f"{self.authors[0]} et al."
        else:
            # Use domain name from URL if no authors
            from urllib.parse import urlparse

            domain = urlparse(self.url).netloc
            author_text = domain

        # Year formatting
        year_text = f"({self.publication_date.year})" if self.publication_date else ""

        return f"{author_text} {year_text}".strip()

    def format_harvard_reference(self) -> str:
        """Format the full reference in Harvard style."""
        # Author formatting
        author_text = ""
        if self.authors:
            if len(self.authors) == 1:
                author_text = self.authors[0]
            elif len(self.authors) <= 3:
                author_text = ", ".join(self.authors[:-1]) + f" and {self.authors[-1]}"
            else:
                author_text = f"{self.authors[0]} et al."
        else:
            # Use domain name from URL if no authors
            from urllib.parse import urlparse

            domain = urlparse(self.url).netloc
            author_text = domain

        # Year formatting
        year_text = f"({self.publication_date.year})" if self.publication_date else ""

        # Title and venue
        title_text = self.title or "Untitled"
        venue_text = f". {self.venue}" if self.venue else ""

        # Format the full reference
        from datetime import datetime

        current_date = datetime.now().strftime("%d %B %Y")

        # Ensure no extra space when year_text is empty
        author_year = f"{author_text} {year_text}".strip()

        return f"{author_year}. {title_text}{venue_text}. [Online] Available at: {self.url} [Accessed: {current_date}]"
