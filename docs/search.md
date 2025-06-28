# Search Helper

The search helper provides a unified interface for different search providers, allowing you to retrieve information from various sources on the web. This document explains how to use the search functionality, the available providers, and their differences.

## Overview

The search helper allows you to:

- Search the web using different providers (DuckDuckGo, Google, Wikipedia, Tavily)
- Filter results by source type (news, professional, regulatory, etc.)
- Limit the number of results
- Include Wikipedia results based on query context
- Deduplicate and rank search results
- Process search requests in parallel for faster response times

## Available Search Providers

RiskGPT supports the following search providers:

| Provider | Description | API Key Required | Full Text | Region Support |
|----------|-------------|------------------|-----------|----------------|
| DuckDuckGo | General web search engine with good privacy | No | No (snippets only) | Yes |
| Google | Google Custom Search Engine | Yes (GOOGLE_CSE_ID and GOOGLE_API_KEY) | No (snippets only) | No |
| Wikipedia | Encyclopedia search | No | No (summaries only) | No |
| Tavily | AI-powered search engine | Yes (TAVILY_API_KEY) | Yes (raw content) | No |

### Provider Comparison

#### Content Returned
- **DuckDuckGo**: Returns snippets of content from the search results
- **Google**: Returns snippets of content from the search results
- **Wikipedia**: Returns summaries of Wikipedia articles
- **Tavily**: Returns the full raw content of the search results

#### Source/Topic Handling
- **DuckDuckGo**: 
  - Supports "news" as a direct source type
  - For other source types, uses "text" as the source and prepends the source type to the query
- **Google**: 
  - Prepends the source type to the query for all searches
- **Wikipedia**: 
  - Doesn't use the source type in the query
- **Tavily**: 
  - Supports "general", "news", "finance" as direct topics
  - For other source types, uses "general" as the topic and prepends the source type to the query

#### Region Support
- **DuckDuckGo**: Supports region filtering via the `region` parameter
- **Google**: Does not use the region parameter
- **Wikipedia**: Does not use the region parameter
- **Tavily**: Does not use the region parameter

#### Date Information
- **DuckDuckGo**: Provides date information when available
- **Google**: Does not provide date information
- **Wikipedia**: Does not provide date information
- **Tavily**: Provides publication date information

#### Relevance Score
- **DuckDuckGo**: Does not provide a relevance score
- **Google**: Does not provide a relevance score
- **Wikipedia**: Does not provide a relevance score
- **Tavily**: Provides a relevance score for each result

## Configuration

The search helper is configured using environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `SEARCH_PROVIDER` | `duckduckgo` | The primary search provider to use. Options: `duckduckgo`, `google`, `wikipedia`, `tavily` |
| `MAX_SEARCH_RESULTS` | `3` | Maximum number of search results to return |
| `INCLUDE_WIKIPEDIA` | `False` | Master toggle for Wikipedia integration |
| `WIKIPEDIA_CONTEXT_AWARE` | `True` | Enable/disable context-based Wikipedia inclusion |
| `WIKIPEDIA_MAX_RESULTS` | `2` | Maximum number of Wikipedia results to include |
| `GOOGLE_CSE_ID` | – | Google Custom Search Engine ID. Required when `SEARCH_PROVIDER` is set to `google` |
| `GOOGLE_API_KEY` | – | Google API key. Required when `SEARCH_PROVIDER` is set to `google` |
| `TAVILY_API_KEY` | – | Tavily API key. Required when `SEARCH_PROVIDER` is set to `tavily` |

## Usage

### Basic Usage

```python
from riskgpt.helpers.search import search, SearchRequest
from riskgpt.models.enums import TopicEnum

# Create a search request
request = SearchRequest(
    query="latest developments in AI regulation",
    source_type=TopicEnum.NEWS,
    max_results=3
)

# Perform the search
response = search(request)

# Process the results
if response.success:
    for result in response.results:
        print(f"Title: {result.title}")
        print(f"URL: {result.url}")
        print(f"Content: {result.content}")
        print("---")
else:
    print(f"Search failed: {response.error_message}")
```

### Using Region with DuckDuckGo

```python
from riskgpt.helpers.search import search, SearchRequest
from riskgpt.models.enums import TopicEnum

# Create a search request with region
request = SearchRequest(
    query="local business regulations",
    source_type=TopicEnum.REGULATORY,
    max_results=3,
    region="us-en"  # Use US English results
)

# Perform the search
response = search(request)
```

### Using Contextual Wikipedia Integration

```python
from riskgpt.helpers.search import search
from riskgpt.models.helpers.search import SearchRequest
from riskgpt.models.enums import TopicEnum

# Create a search request for a knowledge-seeking query
# This will automatically include Wikipedia results due to the nature of the query
request = SearchRequest(
    query="what is artificial intelligence",
    source_type=TopicEnum.NEWS,
    max_results=5
)

# Perform the search
response = search(request)

# Process the results
for result in response.results:
    print(f"Title: {result.title}")
    print(f"URL: {result.url}")
    print(f"Content: {result.content}")
    print("---")
```

## Best Practices

- **Choose the right provider**: 
  - Use **Tavily** when you need the full content of search results
  - Use **DuckDuckGo** when you need region-specific results
  - Use **Google** when you need highly relevant results and have API keys
  - Use **Wikipedia** when you need encyclopedic information

- **Set appropriate source types**:
  - Use `TopicEnum.NEWS` for news articles
  - Use `TopicEnum.PROFESSIONAL` for professional or industry sources
  - Use `TopicEnum.REGULATORY` for regulatory information
  - Use `TopicEnum.PEER` for peer-reviewed or academic sources

- **Limit results appropriately**:
  - Set `max_results` to a reasonable number to avoid excessive API usage
  - Remember that some providers may charge based on the number of results

## Advanced Features

### Result Deduplication

Search results from different providers are automatically deduplicated to avoid showing the same information multiple times. The deduplication process:
- Removes exact URL duplicates
- Detects and removes results with highly similar content

```python
from riskgpt.helpers.search.utils import deduplicate_results
from riskgpt.models.helpers.search import SearchResult

# Example usage
results = [
    SearchResult(title="Result 1", url="http://example.com", content="Content 1"),
    SearchResult(title="Result 2", url="http://example.com/", content="Content 2"),
    SearchResult(title="Result 3", url="http://other.com", content="Content 3"),
]
deduplicated = deduplicate_results(results)
```

### Parallel Processing

Search requests to different providers run in parallel, reducing the overall response time. This is handled automatically by the `search` function when multiple providers are used.

### Contextual Wikipedia Integration

Wikipedia results are included based on the context of the query:
- Automatically included for general knowledge queries
- Less likely to be included for very recent news
- Can be controlled via settings

The contextual inclusion is determined by analyzing:
- If the query contains knowledge-seeking keywords (e.g., "what is", "explain", "definition")
- If the query is for regulatory information (always includes Wikipedia)
- If the query is for recent news (excludes Wikipedia for time-sensitive queries)

### Result Ranking

Search results are ranked based on:
- Relevance score from the provider
- Source type reliability
- Special handling for Wikipedia results

```python
from riskgpt.helpers.search.utils import rank_results
from riskgpt.models.helpers.search import SearchResult

# Example usage
results = [
    SearchResult(title="News", url="http://news.com", type="news", score=1.0),
    SearchResult(title="Regulatory", url="http://reg.com", type="regulatory", score=1.0),
    SearchResult(title="Wiki", url="http://wikipedia.org/wiki/Test", type="news", score=1.0),
]
ranked = rank_results(results)
```

## Error Handling

The search helper includes built-in error handling with circuit breakers to prevent cascading failures. If a search provider fails, it will return an error response with `success=False` and an error message.

```python
response = search(request)
if not response.success:
    # Handle the error
    print(f"Search failed: {response.error_message}")
    # Fallback to another provider or strategy
```
