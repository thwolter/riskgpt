from collections import defaultdict
from difflib import SequenceMatcher
from typing import List

from riskgpt.models.chains.keypoints import KeyPoint


class KeyPointDeduplicator:
    """
    A class for de-duplicating key points extracted from various sources.

    This class provides methods to:
    1. Remove exact duplicates based on content
    2. Group key points by content and combine their sources
    3. Detect and merge similar (non-exact) key points using fuzzy matching
    """

    def __init__(self, key_points: List[KeyPoint], similarity_threshold: float = 0.85):
        """
        Initialize the KeyPointDeduplicator with a list of key points.

        Args:
            key_points: List of KeyPoint objects to de-duplicate
            similarity_threshold: Threshold for considering two key points as similar (0.0 to 1.0)
        """
        self.key_points = key_points
        self.similarity_threshold = similarity_threshold

    def deduplicate(self) -> List[KeyPoint]:
        """
        Perform full de-duplication process on the key points.

        Returns:
            List of de-duplicated KeyPoint objects
        """
        # Step 1: De-duplicate exact matches
        exact_deduplicated = self._deduplicate_exact_matches()

        # Step 2: Detect and merge similar key points
        fuzzy_deduplicated = self._deduplicate_similar_points(exact_deduplicated)

        return fuzzy_deduplicated

    def _deduplicate_exact_matches(self) -> List[KeyPoint]:
        """
        De-duplicate exact matches based on content and group their sources.

        Returns:
            List of KeyPoint objects with exact duplicates removed
        """
        # Group key points by content
        content_to_points = defaultdict(list)
        for point in self.key_points:
            content_to_points[point.content].append(point)

        # Create de-duplicated key points with grouped sources
        deduplicated_points = []

        for content, points in content_to_points.items():
            if len(points) > 1:
                # Multiple sources for the same content - combine them
                combined_point = points[0].model_copy(
                    deep=True
                )  # Use the first point as base

                # Create a list of all source URLs for this content
                source_urls = [p.source_url for p in points if p.source_url]

                # Keep the first URL as the primary source_url
                combined_point.source_url = source_urls[0] if source_urls else None

                # Store additional sources if available
                if (
                    hasattr(combined_point, "additional_sources")
                    and len(source_urls) > 1
                ):
                    combined_point.additional_sources = source_urls[1:]

                deduplicated_points.append(combined_point)
            else:
                # Single source - keep as is
                deduplicated_points.append(points[0])

        return deduplicated_points

    def _deduplicate_similar_points(self, key_points: List[KeyPoint]) -> List[KeyPoint]:
        """
        Detect and merge similar (non-exact) key points using fuzzy matching.

        Args:
            key_points: List of KeyPoint objects with exact duplicates already removed

        Returns:
            List of KeyPoint objects with similar points merged
        """
        if len(key_points) <= 1:
            return key_points

        # Make a copy to avoid modifying the input list during iteration
        result_points = key_points.copy()

        i = 0
        while i < len(result_points):
            j = i + 1
            while j < len(result_points):
                # Check similarity between points i and j
                similarity = SequenceMatcher(
                    None, result_points[i].content, result_points[j].content
                ).ratio()

                if similarity >= self.similarity_threshold:
                    # Merge similar points - keep the longer content
                    if len(result_points[j].content) > len(result_points[i].content):
                        result_points[i].content = result_points[j].content

                    # If they have different source URLs, keep track of both
                    if (
                        result_points[j].source_url
                        and result_points[j].source_url != result_points[i].source_url
                    ):
                        # Add the source URL from point j to point i's additional sources
                        if hasattr(result_points[i], "additional_sources"):
                            if (
                                result_points[j].source_url
                                and result_points[j].source_url
                                not in result_points[i].additional_sources
                            ):
                                result_points[i].additional_sources.append(
                                    result_points[j].source_url  # type: ignore[arg-type]
                                )

                    # Remove the duplicate
                    result_points.pop(j)
                else:
                    j += 1
            i += 1

        return result_points
