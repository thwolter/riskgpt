from __future__ import annotations

from typing import Annotated, Any, List, TypedDict

from langgraph.graph import END, StateGraph, add_messages
from models.enums import TopicEnum
from models.workflows.context import ExtractKeyPointsResponse

from src.models.base import ResponseInfo
from src.models.workflows.context import ExternalContextRequest, ExternalContextResponse
from src.utils.extraction import extract_key_points
from src.utils.search import search


class State(dict[str, List[Any]]
):
    messages: Annotated[list, add_messages]

    sources: List[dict]
    news_sources: List[dict]
    linkedin_sources: List[dict]
    regulatory_sources: List[dict]

    news_key_points: List[str]
    linkedin_key_points: List[str]
    regulatory_key_points: List[str]

    search_failed: bool
    response_info_list: List[ResponseInfo]
    response: ExternalContextResponse


def topic_search(
    state: State, request: ExternalContextRequest, topic: TopicEnum
) -> State:
    query = f"{request.business_context.project_description} {request.business_context.domain_knowledge or ''} {topic.value}"
    key = topic.source_key()

    if request.focus_keywords:
        query += " " + " ".join(request.focus_keywords)
    res, ok = search(query, topic.value)

    existing_urls = {item["url"] for item in state.get("sources", [])}
    new_items = [item for item in res if item["url"] not in existing_urls]

    state.setdefault("sources", []).extend(new_items)
    state.setdefault(key, []).extend(new_items)  # type: ignore[misc]

    if not ok:
        state["search_failed"] = True
    return state


async def extract_topic_key_points(state: State, topic: TopicEnum) -> State:
    sources: List[Any] = state.get(topic.source_key(), [])  # type: ignore[misc]
    key_points = []

    for source in sources:
        result: ExtractKeyPointsResponse = await extract_key_points(source, topic.value)
        state.setdefault("response_info_list", []).append(result.response_info)
        for point in result.points:
            key_points.append(point)

    state[topic.key_points_key()] = key_points  # type: ignore[misc]
    return state


def aggregate_response_info(state):
    total_tokens = 0
    total_cost = 0.0
    model_name = ""
    response_info_list = state.get("response_info_list", [])
    if response_info_list:
        total_cost = sum(info.total_cost for info in response_info_list)
        total_tokens = sum(info.consumed_tokens for info in response_info_list)
        model_name = response_info_list[-1].model_name
    return ResponseInfo(
        consumed_tokens=total_tokens,
        total_cost=total_cost,
        prompt_name="external_context_enrichment",
        model_name=model_name,
    )


def _build_graph(request: ExternalContextRequest):
    graph = StateGraph(State)

    def news_search(state: State) -> State:
        return topic_search(state, request, TopicEnum.NEWS)

    def professional_search(state: State) -> State:
        return topic_search(state, request, TopicEnum.LINKEDIN)

    def regulatory_search(state: State) -> State:
        return topic_search(state, request, TopicEnum.REGULATORY)

    async def extract_news_key_points(state: State) -> State:
        return await extract_topic_key_points(state, TopicEnum.NEWS)

    async def extract_professional_key_points(state: State) -> State:
        return await extract_topic_key_points(state, TopicEnum.LINKEDIN)

    async def extract_regulatory_key_points(state: State) -> State:
        return await extract_topic_key_points(state, TopicEnum.REGULATORY)

    async def summarise(state: State) -> State:
        sources = state.get("sources", [])

        for src in sources:
            if src.get("comment") is None:
                src["comment"] = ""

        # Collect all key points from different source types
        all_key_points = (
            state.get(f"{TopicEnum.NEWS.value.lower()}_key_points", [])
            + state.get(f"{TopicEnum.LINKEDIN.value.lower()}_key_points", [])
            + state.get(f"{TopicEnum.REGULATORY.value.lower()}_key_points", [])
        )

        if not sources:
            if state.get("search_failed"):
                summary = "No external data retrieved due to network restrictions or missing dependencies"
            else:
                summary = "No recent relevant information found"
            key_points = []
            recs: List[str] = []
        else:
            summary = f"Collected {len(sources)} external sources for {request.business_context.project_id}."
            # Use extracted key points for risks if available
            if all_key_points:
                key_points = all_key_points
            else:
                key_points = [f"Potential issue: {s['title']}" for s in sources[:3]]

            recs = [f"Review source: {s['title']}" for s in sources[:2]]

        resp = ExternalContextResponse(
            sector_summary=summary,
            key_points=key_points,
            source_table=sources,
            workshop_recommendations=recs,
            full_report=None,
        )
        resp.response_info = aggregate_response_info(state)

        state["response"] = resp
        return state

    # Add nodes to the graph
    graph.add_node("news", news_search)
    graph.add_node("professional", professional_search)
    graph.add_node("regulatory", regulatory_search)
    graph.add_node("extract_news_key_points", extract_news_key_points)
    graph.add_node("extract_professional_key_points", extract_professional_key_points)
    graph.add_node("extract_regulatory_key_points", extract_regulatory_key_points)
    graph.add_node("summarise", summarise)

    # Set up the graph with parallel processing
    graph.set_entry_point("news")

    # After each search, extract key points from that source type
    graph.add_edge("news", "extract_news_key_points")
    graph.add_edge("extract_news_key_points", "professional")

    graph.add_edge("professional", "extract_professional_key_points")
    graph.add_edge("extract_professional_key_points", "regulatory")

    graph.add_edge("regulatory", "extract_regulatory_key_points")
    graph.add_edge("extract_regulatory_key_points", "summarise")

    graph.add_edge("summarise", END)

    return graph.compile()


async def enrich_context(
    request: ExternalContextRequest,
) -> ExternalContextResponse:
    """Run the external context enrichment workflow asynchronously."""

    app = _build_graph(request)
    result = await app.ainvoke({})
    return result["response"]
