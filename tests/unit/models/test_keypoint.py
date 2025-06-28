from datetime import date

from riskgpt.models.chains.keypoints import KeyPoint
from riskgpt.models.enums import TopicEnum
from riskgpt.models.helpers.citation import Citation


class TestKeyPoint:
    def test_get_inline_citation_with_citation(self):
        citation = Citation(
            url="https://example.com",
            title="Example Title",
            authors=["John Doe"],
            publication_date=date(2023, 1, 1),
            venue="Example Venue",
        )

        keypoint = KeyPoint(
            content="This is a key point",
            topic=TopicEnum.NEWS,
            source_url="https://example.com",
            citation=citation,
        )

        result = keypoint.get_inline_citation()
        assert result == "John Doe (2023)"

    def test_get_inline_citation_without_citation_with_source_url(self):
        keypoint = KeyPoint(
            content="This is a key point",
            topic=TopicEnum.NEWS,
            source_url="https://example.com",
        )

        result = keypoint.get_inline_citation()
        assert result == "example.com"

    def test_get_inline_citation_without_citation_or_source_url(self):
        keypoint = KeyPoint(
            content="This is a key point",
            topic=TopicEnum.NEWS,
        )

        result = keypoint.get_inline_citation()
        assert result == ""
