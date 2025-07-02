from datetime import date

from pydantic import HttpUrl

from riskgpt.models.chains.keypoints import KeyPoint
from riskgpt.models.enums import ScopeEnum
from riskgpt.models.helpers.citation import Citation
from riskgpt.workflows.research.deduplicator import KeyPointDeduplicator


class TestKeyPointDeduplicator:
    """Tests for the KeyPointDeduplicator class."""

    def create_test_keypoint(
        self, content: str, url: str, title: str = "Test Title"
    ) -> KeyPoint:
        """Helper method to create a test KeyPoint."""
        citation = Citation(
            url=HttpUrl(url),
            title=title,
            authors=["Test Author"],
            publication_date=date(2023, 1, 1),
            venue="Test Venue",
            publisher="Test Publisher",
        )
        return KeyPoint(
            content=content,
            scope=ScopeEnum.NEWS,
            citation=citation,
            additional_sources=[],
        )

    def test_init(self):
        """Test initialization of KeyPointDeduplicator."""
        key_points = [
            self.create_test_keypoint("Test content", "https://example.com/1"),
            self.create_test_keypoint("Another content", "https://example.com/2"),
        ]
        deduplicator = KeyPointDeduplicator(key_points, similarity_threshold=0.85)

        assert deduplicator.key_points == key_points
        assert deduplicator.similarity_threshold == 0.85

    def test_deduplicate_exact_matches(self):
        """Test deduplication of exact matches."""
        # Create key points with exact duplicate content but different sources
        key_points = [
            self.create_test_keypoint("Duplicate content", "https://example.com/1"),
            self.create_test_keypoint("Duplicate content", "https://example.com/2"),
            self.create_test_keypoint("Unique content", "https://example.com/3"),
        ]

        deduplicator = KeyPointDeduplicator(key_points)
        result = deduplicator._deduplicate_exact_matches()

        # Should have 2 key points after deduplication (1 combined + 1 unique)
        assert len(result) == 2

        # Find the deduplicated point
        deduplicated_point = next(
            (p for p in result if p.content == "Duplicate content"), None
        )
        assert deduplicated_point is not None
        assert str(deduplicated_point.citation.url) == "https://example.com/1"
        assert "https://example.com/2" in deduplicated_point.additional_sources

    def test_deduplicate_similar_points(self):
        """Test deduplication of similar (non-exact) key points."""
        # Create key points with similar content
        key_points = [
            self.create_test_keypoint(
                "AI technology is advancing rapidly in 2023.", "https://example.com/1"
            ),
            self.create_test_keypoint(
                "AI technology is advancing very rapidly in the year 2023.",
                "https://example.com/2",
            ),
            self.create_test_keypoint(
                "Completely different content about climate change.",
                "https://example.com/3",
            ),
        ]

        deduplicator = KeyPointDeduplicator(key_points, similarity_threshold=0.8)
        result = deduplicator._deduplicate_similar_points(key_points)

        # Should have 2 key points after deduplication (1 merged + 1 unique)
        assert len(result) == 2

        # The longer content should be kept
        similar_point = next((p for p in result if "AI technology" in p.content), None)
        assert similar_point is not None
        assert (
            similar_point.content
            == "AI technology is advancing very rapidly in the year 2023."
        )
        assert (
            "https://example.com/1" in similar_point.additional_sources
            or str(similar_point.citation.url) == "https://example.com/1"
        )

    def test_full_deduplication_process(self):
        """Test the full deduplication process."""
        # Create a mix of exact and similar key points
        key_points = [
            self.create_test_keypoint("Exact duplicate", "https://example.com/1"),
            self.create_test_keypoint("Exact duplicate", "https://example.com/2"),
            self.create_test_keypoint(
                "Similar content about machine learning", "https://example.com/3"
            ),
            self.create_test_keypoint(
                "Very similar content about machine learning algorithms",
                "https://example.com/4",
            ),
            self.create_test_keypoint("Unique content", "https://example.com/5"),
        ]

        deduplicator = KeyPointDeduplicator(key_points, similarity_threshold=0.7)
        result = deduplicator.deduplicate()

        # Should have 3 key points after full deduplication
        # (1 exact duplicate + 1 similar merged + 1 unique)
        assert len(result) == 3

    def test_empty_list(self):
        """Test deduplication with an empty list."""
        deduplicator = KeyPointDeduplicator([])
        result = deduplicator.deduplicate()
        assert result == []

    def test_single_item(self):
        """Test deduplication with a single item."""
        key_point = self.create_test_keypoint("Single item", "https://example.com/1")
        deduplicator = KeyPointDeduplicator([key_point])
        result = deduplicator.deduplicate()
        assert len(result) == 1
        assert result[0].content == "Single item"

    def test_different_similarity_thresholds(self):
        """Test deduplication with different similarity thresholds."""
        # Create key points with very different content for high threshold test
        high_threshold_key_points = [
            self.create_test_keypoint(
                "AI technology is advancing rapidly in 2023.", "https://example.com/1"
            ),
            self.create_test_keypoint(
                "Climate change is affecting global temperatures.",
                "https://example.com/2",
            ),
        ]

        # With high threshold, should not deduplicate very different content
        high_threshold_deduplicator = KeyPointDeduplicator(
            high_threshold_key_points, similarity_threshold=0.9
        )
        high_result = high_threshold_deduplicator.deduplicate()
        assert len(high_result) == 2

        # Create key points with similar content for low threshold test
        low_threshold_key_points = [
            self.create_test_keypoint(
                "AI technology is advancing rapidly in 2023.", "https://example.com/1"
            ),
            self.create_test_keypoint(
                "AI technology is advancing quickly in 2023.", "https://example.com/2"
            ),
        ]

        # With low threshold, should deduplicate similar content
        low_threshold_deduplicator = KeyPointDeduplicator(
            low_threshold_key_points, similarity_threshold=0.5
        )
        low_result = low_threshold_deduplicator.deduplicate()
        assert len(low_result) == 1
