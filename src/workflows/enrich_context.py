from __future__ import annotations

from typing import Annotated, List, TypedDict

from langgraph.graph import END, StateGraph, add_messages

from src.api import search_context
from src.models.base import ResponseInfo
from src.models.workflows.context import ExternalContextRequest, ExternalContextResponse
from src.utils.extraction import extract_key_points


class State(TypedDict):
    messages: Annotated[list, add_messages]
    sources: List[dict]
    news_sources: List[dict]
    professional_sources: List[dict]
    regulatory_sources: List[dict]
    peer_sources: List[dict]
    news_key_points: List[str]
    professional_key_points: List[str]
    regulatory_key_points: List[str]
    peer_key_points: List[str]
    search_failed: bool
    response_info_list: List[ResponseInfo]
    response: ExternalContextResponse


def _build_graph(request: ExternalContextRequest):
    graph = StateGraph(State)

    def news_search(state: State) -> State:
        query = f"{request.business_context.project_description} {request.business_context.domain_knowledge or ''} news"
        if request.focus_keywords:
            query += " " + " ".join(request.focus_keywords)
        res, ok = search_context(query, "news")
        state["sources"].extend(res)
        state["news_sources"] = res
        if not ok:
            state["search_failed"] = True
        return state

    def professional_search(state: State) -> State:
        query = f"{request.business_context.project_description} {request.business_context.domain_knowledge or ''} LinkedIn"
        res, ok = search_context(query, "social")
        state["sources"].extend(res)
        state["professional_sources"] = res
        if not ok:
            state["search_failed"] = True
        return state

    def regulatory_search(state: State) -> State:
        query = f"{request.business_context.domain_knowledge or request.business_context.project_description} regulation"
        res, ok = search_context(query, "regulation")
        state["sources"].extend(res)
        state["regulatory_sources"] = res
        if not ok:
            state["search_failed"] = True
        return state

    def peer_search(state: State) -> State:
        query = f"{request.business_context.domain_knowledge or request.business_context.project_description} competitor incident"
        res, ok = search_context(query, "peer")
        state["sources"].extend(res)
        state["peer_sources"] = res
        if not ok:
            state["search_failed"] = True
        return state

    async def extract_news_key_points(state: State) -> State:
        sources = state.get("news_sources", [])
        key_points = []

        for source in sources:
            # Extract key points using LLM and get response info
            points, response_info = await extract_key_points(source, "news")

            # Store response info
            state["response_info_list"].append(response_info)

            for point in points:
                key_points.append(f"News: {point}")

        state["news_key_points"] = key_points
        return state

    async def extract_professional_key_points(state: State) -> State:
        sources = state.get("professional_sources", [])
        key_points = []

        for source in sources:
            # Extract key points using LLM and get response info
            points, response_info = await extract_key_points(source, "professional")

            # Store response info
            state["response_info_list"].append(response_info)

            for point in points:
                key_points.append(f"Professional: {point}")

        state["professional_key_points"] = key_points
        return state

    async def extract_regulatory_key_points(state: State) -> State:
        sources = state.get("regulatory_sources", [])
        key_points = []

        for source in sources:
            # Extract key points using LLM and get response info
            points, response_info = await extract_key_points(source, "regulatory")

            # Store response info
            state["response_info_list"].append(response_info)

            for point in points:
                key_points.append(f"Regulatory: {point}")

        state["regulatory_key_points"] = key_points
        return state

    async def extract_peer_key_points(state: State) -> State:
        sources = state.get("peer_sources", [])
        key_points = []

        for source in sources:
            # Extract key points using LLM and get response info
            points, response_info = await extract_key_points(source, "peer")

            # Store response info
            state["response_info_list"].append(response_info)

            for point in points:
                key_points.append(f"Peer: {point}")

        state["peer_key_points"] = key_points
        return state

    async def summarise(state: State) -> State:
        sources = state.get("sources", [])

        # Collect all key points from different source types
        all_key_points = (
            state.get("news_key_points", [])
            + state.get("professional_key_points", [])
            + state.get("regulatory_key_points", [])
            + state.get("peer_key_points", [])
        )

        # Calculate total cost and get model name
        total_tokens = 0
        total_cost = 0.0
        model_name = ""

        # Get response info from the list
        response_info_list = state.get("response_info_list", [])
        if response_info_list:
            # Sum up the costs
            total_cost = sum(info.total_cost for info in response_info_list)
            # Sum up the tokens
            total_tokens = sum(info.consumed_tokens for info in response_info_list)
            # Use the model name from the last response
            model_name = response_info_list[-1].model_name

        if not sources:
            if state.get("search_failed"):
                summary = "No external data retrieved due to network restrictions or missing dependencies"
            else:
                summary = "No recent relevant information found"
            risks: List[str] = []
            recs: List[str] = []
        else:
            summary = f"Collected {len(sources)} external sources for {request.business_context.project_description or request.business_context.project_id}."
            # Use extracted key points for risks if available
            if all_key_points:
                risks = all_key_points[:5]  # Use top 5 key points as risks
            else:
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
            consumed_tokens=total_tokens,
            total_cost=total_cost,
            prompt_name="external_context_enrichment",
            model_name=model_name,
        )
        state["response"] = resp
        return state

    # Add nodes to the graph
    graph.add_node("news", news_search)
    graph.add_node("professional", professional_search)
    graph.add_node("regulatory", regulatory_search)
    graph.add_node("peer", peer_search)
    graph.add_node("extract_news_key_points", extract_news_key_points)
    graph.add_node("extract_professional_key_points", extract_professional_key_points)
    graph.add_node("extract_regulatory_key_points", extract_regulatory_key_points)
    graph.add_node("extract_peer_key_points", extract_peer_key_points)
    graph.add_node("summarise", summarise)

    # Set up the graph with parallel processing
    graph.set_entry_point("news")

    # After each search, extract key points from that source type
    graph.add_edge("news", "extract_news_key_points")
    graph.add_edge("extract_news_key_points", "professional")

    graph.add_edge("professional", "extract_professional_key_points")
    graph.add_edge("extract_professional_key_points", "regulatory")

    graph.add_edge("regulatory", "extract_regulatory_key_points")
    graph.add_edge("extract_regulatory_key_points", "peer")

    graph.add_edge("peer", "extract_peer_key_points")
    graph.add_edge("extract_peer_key_points", "summarise")

    graph.add_edge("summarise", END)

    return graph.compile()


async def enrich_context(
    request: ExternalContextRequest,
) -> ExternalContextResponse:
    """Run the external context enrichment workflow asynchronously."""

    app = _build_graph(request)
    result = await app.ainvoke(
        {
            "sources": [],
            "news_sources": [],
            "professional_sources": [],
            "regulatory_sources": [],
            "peer_sources": [],
            "news_key_points": [],
            "professional_key_points": [],
            "regulatory_key_points": [],
            "peer_key_points": [],
            "response_info_list": [],
        }
    )
    return result["response"]
