# Extract Keywords Chain

The Extract Keywords Chain provides functionality to extract the most important keywords or phrases from a long text query. This is particularly useful for optimizing search queries by focusing on the most relevant terms.

## Overview

The Extract Keywords Chain allows you to:

- Extract the most important keywords from a long text query
- Specify the maximum number of keywords to extract
- Use the extracted keywords for more effective search queries

## How It Works

The chain uses a language model to analyze the input text and identify the most important keywords or phrases. It's designed to:

1. Process the input text to understand its content
2. Identify the most relevant terms based on the context
3. Return a concise set of keywords that capture the essence of the query

This is particularly useful when dealing with long, complex queries that might contain a lot of non-essential information. By extracting only the key terms, search engines can focus on the most relevant content.

## Usage

### Async Usage

```python
from riskgpt.chains import extract_keywords_chain
from riskgpt.models.chains.keywords import ExtractKeywordsRequest

# Create a request
request = ExtractKeywordsRequest(
    query="Recent developments in artificial intelligence have shown promising applications in risk management. Companies are increasingly using AI to identify potential risks in their operations and to automate risk assessment processes.",
    max_keywords=5
)

# Call the chain
response = await extract_keywords_chain(request)

# Get the extracted keywords
keywords = response.keywords
print(f"Extracted keywords: {keywords}")
```

### Synchronous Usage

For convenience, a synchronous wrapper is also provided:

```python
from riskgpt.chains.extract_keywords import extract_keywords

# Extract keywords from a long query
keywords = extract_keywords(
    query="Recent developments in artificial intelligence have shown promising applications in risk management. Companies are increasingly using AI to identify potential risks in their operations and to automate risk assessment processes.",
    max_keywords=5
)

print(f"Extracted keywords: {keywords}")
```

## Integration with Search

The Extract Keywords Chain is particularly useful when integrated with search functionality. For example, the Semantic Scholar search provider automatically uses this chain to optimize long queries:

```python
from riskgpt.helpers.search import search, SearchRequest
from riskgpt.models.enums import TopicEnum

# Create a search request with a long query
request = SearchRequest(
    query="Recent developments in artificial intelligence have shown promising applications in risk management. Companies are increasingly using AI to identify potential risks in their operations and to automate risk assessment processes.",
    source_type=TopicEnum.ACADEMIC,
    max_results=3
)

# The search function will automatically extract keywords for long queries
response = search(request)
```

## Models

### ExtractKeywordsRequest

The request model for the Extract Keywords Chain:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `query` | `str` | Required | The query text to extract keywords from |
| `max_keywords` | `int` | `5` | Maximum number of keywords to extract |

### ExtractKeywordsResponse

The response model for the Extract Keywords Chain:

| Field | Type | Description |
|-------|------|-------------|
| `keywords` | `str` | The extracted keywords separated by spaces |
| `response_info` | `ResponseInfo` | Information about the response processing |

## Performance Considerations

- The chain uses an LLM call, so there is a cost and latency associated with each extraction
- For very short queries (e.g., less than 20 words), keyword extraction may not be necessary
- The quality of extracted keywords depends on the quality and clarity of the input text