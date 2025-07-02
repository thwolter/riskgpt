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

                # Collect all citations for this content
                all_citations = []
                for p in points:
                    if hasattr(p, "citations"):
                        all_citations.extend(p.citations)

                # Set the combined citations
                combined_point.citations = all_citations

                # Create a list of all source URLs for this content
                source_urls = []
                for citation in all_citations:
                    if citation and citation.url:
                        url_str = str(citation.url)
                        if url_str not in source_urls:
                            source_urls.append(url_str)

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

                    # Merge citations from point j into point i
                    j_citations = (
                        result_points[j].citations
                        if hasattr(result_points[j], "citations")
                        else []
                    )

                    # Add citations from point j to point i
                    for citation in j_citations:
                        if citation not in result_points[i].citations:
                            result_points[i].citations.append(citation)

                    # Remove the duplicate
                    result_points.pop(j)
                else:
                    j += 1
            i += 1

        return result_points
