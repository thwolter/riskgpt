from __future__ import annotations

from typing import Any, Dict, List

from riskgpt.logger import logger
from riskgpt.models.schemas import (
    ExternalContextRequest,
    ExternalContextResponse,
    ResponseInfo,
)

try:
    from langgraph.graph import END, StateGraph
except Exception:  # pragma: no cover - optional dependency
    END = None
    StateGraph = None

try:
    from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
except Exception:  # pragma: no cover - optional dependency
    DuckDuckGoSearchAPIWrapper = None


def _search(query: str, source_type: str) -> List[Dict[str, str]]:
    """Perform a DuckDuckGo search and format results."""
    results: List[Dict[str, str]] = []
    if DuckDuckGoSearchAPIWrapper is None:
        logger.warning("duckduckgo-search not available")
        return results
    try:
        wrapper = DuckDuckGoSearchAPIWrapper()
        for item in wrapper.results(query, max_results=3):
            results.append(
                {
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "date": item.get("date"),
                    "type": source_type,
                    "comment": item.get("snippet", ""),
                }
            )
    except Exception as exc:  # pragma: no cover - search failure should not crash
        logger.error("Search failed: %s", exc)
    return results


def _build_graph(request: ExternalContextRequest):
    if StateGraph is None:
        raise ImportError("langgraph is required for this workflow")

    graph = StateGraph(Dict[str, Any])

    def news_search(state: Dict[str, Any]) -> Dict[str, Any]:
        query = f"{request.project_name} {request.business_context} news"
        if request.focus_keywords:
            query += " " + " ".join(request.focus_keywords)
        state.setdefault("sources", []).extend(_search(query, "news"))
        return state

    def professional_search(state: Dict[str, Any]) -> Dict[str, Any]:
        query = f"{request.project_name} {request.business_context} LinkedIn"
        state.setdefault("sources", []).extend(_search(query, "social"))
        return state

    def regulatory_search(state: Dict[str, Any]) -> Dict[str, Any]:
        query = f"{request.business_context} regulation"
        state.setdefault("sources", []).extend(_search(query, "regulation"))
        return state

    def peer_search(state: Dict[str, Any]) -> Dict[str, Any]:
        query = f"{request.business_context} competitor incident"
        state.setdefault("sources", []).extend(_search(query, "peer"))
        return state

    def summarise(state: Dict[str, Any]) -> Dict[str, Any]:
        sources = state.get("sources", [])
        if not sources:
            summary = "No recent relevant information found"
            risks: List[str] = []
            recs: List[str] = []
        else:
            summary = f"Collected {len(sources)} external sources for {request.project_name}."
            risks = [f"Potential issue: {s['title']}" for s in sources[:3]]
            recs = [f"Review source: {s['title']}" for s in sources[:2]]
        resp = ExternalContextResponse(
            sector_summary=summary,
            external_risks=risks,
            source_table=sources,
            workshop_recommendations=recs,
            full_report=None,
        )
        resp.response_info = ResponseInfo(
            consumed_tokens=0,
            total_cost=0.0,
            prompt_name="external_context_enrichment",
            model_name="",
        )
        state["response"] = resp
        return state

    graph.add_node("news", news_search)
    graph.add_node("professional", professional_search)
    graph.add_node("regulatory", regulatory_search)
    graph.add_node("peer", peer_search)
    graph.add_node("summarise", summarise)

    graph.set_entry_point("news")
    graph.add_edge("news", "professional")
    graph.add_edge("professional", "regulatory")
    graph.add_edge("regulatory", "peer")
    graph.add_edge("peer", "summarise")
    graph.add_edge("summarise", END)

    return graph.compile()


def external_context_enrichment(request: ExternalContextRequest) -> ExternalContextResponse:
    """Run the external context enrichment workflow."""

    app = _build_graph(request)
    result = app.invoke({})
    return result["response"]
