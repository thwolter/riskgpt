"""Manual test script for search improvements."""

from riskgpt.helpers.search import _should_include_wikipedia
from riskgpt.helpers.search.utils import deduplicate_results, rank_results
from riskgpt.models.enums import TopicEnum
from riskgpt.models.helpers.search import SearchRequest, SearchResult

# Test deduplication
print("Testing deduplication...")
results = [
    SearchResult(title="Result 1", url="http://example.com", content="Content 1"),
    SearchResult(title="Result 2", url="http://example.com/", content="Content 2"),
    SearchResult(title="Result 3", url="http://other.com", content="Content 3"),
]
deduplicated = deduplicate_results(results)
print(f"Original results: {len(results)}")
print(f"Deduplicated results: {len(deduplicated)}")
for result in deduplicated:
    print(f"  - {result.title}: {result.url}")

# Test ranking
print("\nTesting ranking...")
results = [
    SearchResult(title="News", url="http://news.com", type="news", score=1.0),
    SearchResult(
        title="Regulatory", url="http://reg.com", type="regulatory", score=1.0
    ),
    SearchResult(
        title="Wiki", url="http://wikipedia.org/wiki/Test", type="news", score=1.0
    ),
]
ranked = rank_results(results)
print("Ranked results:")
for result in ranked:
    print(f"  - {result.title}: {result.type} (score: {result.score})")

# Test contextual Wikipedia inclusion
print("\nTesting contextual Wikipedia inclusion...")
requests = [
    SearchRequest(query="what is artificial intelligence", source_type=TopicEnum.NEWS),
    SearchRequest(query="latest tech news today", source_type=TopicEnum.NEWS),
    SearchRequest(query="GDPR compliance", source_type=TopicEnum.REGULATORY),
]
for request in requests:
    include = _should_include_wikipedia(request)
    print(
        f"Query: '{request.query}', Type: {request.source_type.value}, Include Wikipedia: {include}"
    )

print("\nManual tests completed successfully!")
