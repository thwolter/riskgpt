"""Public API helpers for external services.

This module exposes thin wrappers around internal utilities
so that workflows and external consumers share a common entry
point for web search and document retrieval.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from riskgpt.logger import logger
from riskgpt.models.schemas import BusinessContext
from riskgpt.utils.search import search as _search


def search_context(query: str, source_type: str) -> Tuple[List[Dict[str, str]], bool]:
    """Search for contextual information using the configured provider.

    This is a simple wrapper around :func:`riskgpt.utils.search.search` that
    can be used directly in applications and workflows.
    """

    return _search(query, source_type)


def fetch_documents(context: BusinessContext) -> List[str]:
    """Fetch document UUIDs relevant to the provided business context.

    The real implementation will call the document microservice.  For now this
    function returns a mocked list of UUIDs so callers can already integrate
    against a stable interface.
    """

    logger.info("Fetching relevant documents for project %s", context.project_id)

    # TODO: Replace with real document service call
    return ["doc-uuid-001", "doc-uuid-002"]


__all__ = ["search_context", "fetch_documents"]
