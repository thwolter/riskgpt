from __future__ import annotations

from typing import Any, Dict, List

from riskgpt.api import search_context
from riskgpt.models.schemas import (
    ExternalContextRequest,
    ExternalContextResponse,
    ResponseInfo,
)

END: Any
StateGraph: Any
try:
    from langgraph.graph import END as _END
    from langgraph.graph import StateGraph as _StateGraph

    END = _END
    StateGraph = _StateGraph
except Exception:  # pragma: no cover - optional dependency
    END = None
    StateGraph = None


def _build_graph(request: ExternalContextRequest):
    if StateGraph is None:
        raise ImportError("langgraph is required for this workflow")

    graph = StateGraph(Dict[str, Any])

    def news_search(state: Dict[str, Any]) -> Dict[str, Any]:
        query = f"{request.business_context.project_description or request.business_context.project_id} {request.business_context.domain_knowledge or ''} news"
        if request.focus_keywords:
            query += " " + " ".join(request.focus_keywords)
        res, ok = search_context(query, "news")
        state.setdefault("sources", []).extend(res)
        if not ok:
            state["search_failed"] = True
        return state

    def professional_search(state: Dict[str, Any]) -> Dict[str, Any]:
        query = f"{request.business_context.project_description or request.business_context.project_id} {request.business_context.domain_knowledge or ''} LinkedIn"
        res, ok = search_context(query, "social")
        state.setdefault("sources", []).extend(res)
        if not ok:
            state["search_failed"] = True
        return state

    def regulatory_search(state: Dict[str, Any]) -> Dict[str, Any]:
        query = f"{request.business_context.domain_knowledge or request.business_context.project_description or request.business_context.project_id} regulation"
        res, ok = search_context(query, "regulation")
        state.setdefault("sources", []).extend(res)
        if not ok:
            state["search_failed"] = True
        return state

    def peer_search(state: Dict[str, Any]) -> Dict[str, Any]:
        query = f"{request.business_context.domain_knowledge or request.business_context.project_description or request.business_context.project_id} competitor incident"
        res, ok = search_context(query, "peer")
        state.setdefault("sources", []).extend(res)
        if not ok:
            state["search_failed"] = True
        return state

    def summarise(state: Dict[str, Any]) -> Dict[str, Any]:
        sources = state.get("sources", [])
        if not sources:
            if state.get("search_failed"):
                summary = "No external data retrieved due to network restrictions or missing dependencies"
            else:
                summary = "No recent relevant information found"
            risks: List[str] = []
            recs: List[str] = []
        else:
            summary = f"Collected {len(sources)} external sources for {request.business_context.project_description or request.business_context.project_id}."
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


def external_context_enrichment(
    request: ExternalContextRequest,
) -> ExternalContextResponse:
    """Run the external context enrichment workflow."""

    app = _build_graph(request)
    result = app.invoke({})
    return result["response"]
