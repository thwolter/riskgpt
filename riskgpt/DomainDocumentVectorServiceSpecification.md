# Domain Document Vector Microservice Specification

This document describes the requirements and endpoints for a future FastAPI microservice that will manage domain document ingestion and vector search for RiskGPT.

## Purpose

- Enable RiskGPT to query and reference relevant project or domain documents for risk assessment through UUIDs.
- Serve document search, vectorization, and metadata retrieval.

## Endpoints

### 1. `/vectorize`
- **Purpose:** Upload new documents or document fragments for vectorization.
- **Request:** File(s) or text, plus optional metadata.
- **Response:** List of assigned document UUIDs.

### 2. `/search`
- **Purpose:** Retrieve relevant document UUIDs for a given query or project context.
- **Request:** Query string or JSON with context fields.
- **Response:** Array of UUIDs with optional scores/metadata.

### 3. `/get/{uuid}`
- **Purpose:** Retrieve metadata, text, or a link to the document by UUID.
- **Request:** Path param: `uuid`
- **Response:** Metadata and/or content summary.

## Integration with RiskGPT

- RiskGPT will pass project or context information to `/search`.
- RiskGPT will store returned UUIDs in the `document_refs` field of risk or assessment objects.

## Other Requirements

- Provide basic authentication.
- Support for scalable vector storage (e.g., using sentence-transformers, FAISS, or similar).
- Usage and error logging for queries and uploads.

---

*For full API contract, OpenAPI documentation will be provided before implementation.*

```