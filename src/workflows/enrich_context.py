from __future__ import annotations

from typing import Annotated, List, TypedDict

from langgraph.graph import END, StateGraph, add_messages
from models.enums import TopicEnum
from models.utils.search import SearchRequest, SearchResponse, Source
from models.workflows.context import (
    ExtractKeyPointsRequest,
    ExtractKeyPointsResponse,
    KeyPoint,
)

from src.chains.keypoint_text import keypoint_text_chain
from src.models.base import ResponseInfo
from src.models.workflows.context import (
    ExternalContextRequest,
    ExternalContextResponse,
    KeyPointTextResponse,
)
from src.utils.extraction import extract_key_points
from src.utils.search import search, settings


class State(TypedDict):
    messages: Annotated[list, add_messages]

    sources: List[Source]
    key_points: List[KeyPoint]

    search_failed: bool
    response_info_list: List[ResponseInfo]
    keypoint_text_response: KeyPointTextResponse
    response: ExternalContextResponse


def topic_search(
    state: State,
    request: ExternalContextRequest,
    topic: TopicEnum,
    max_results: int | None = None,
) -> State:
    if max_results is None:
        max_results = settings.MAX_SEARCH_RESULTS

    query = request.create_search_query()
    request = SearchRequest(
        query=query,
        source_type=topic.value,
        max_results=max_results,
    )
    search_response: SearchResponse = search(request)

    sources: List[Source] = state.get("sources", [])
    existing_urls = {source.url for source in sources}

    # Convert SearchResult objects to Source objects
    new_sources = [
        Source.from_search_result(item, topic)
        for item in search_response.results
        if item.url not in existing_urls
    ]

    state.setdefault("sources", []).extend(new_sources)

    if not search_response.success:
        state["search_failed"] = True
    return state


async def extract_topic_key_points(state: State, topic: TopicEnum) -> State:
    # Filter sources by topic
    sources: List[Source] = state.get("sources", [])
    topic_sources = [source for source in sources if source.topic == topic]

    for source in topic_sources:
        request = ExtractKeyPointsRequest.from_source(source)
        response: ExtractKeyPointsResponse = await extract_key_points(request)

        # Attach source.url to each point in response.points
        for point in response.points:
            point.source_url = source.url

        state.setdefault("response_info_list", []).append(response.response_info)
        state.setdefault("key_points", []).extend(response.points)

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

    async def aggregate(state: State) -> State:
        sources: List[Source] = state.get("sources", [])

        for src in sources:
            if src.content is None:
                src.content = ""

        # Get all key points
        all_key_points: List[KeyPoint] = state.get("key_points", [])

        if not sources:
            if state.get("search_failed"):
                summary = "No external data retrieved due to network restrictions or missing dependencies"
            else:
                summary = "No recent relevant information found"
            key_points_content = []
            recs: List[str] = []
            sorted_sources = []
            full_report = None
        else:
            summary = f"Collected {len(sources)} external sources for {request.business_context.project_id}."

            # Use extracted key points if available
            if all_key_points:
                # Generate text with Harvard-style citations from key points
                keypoint_text_resp: KeyPointTextResponse = await keypoint_text_chain(
                    all_key_points
                )
                state["keypoint_text_response"] = keypoint_text_resp
                state.setdefault("response_info_list", []).append(
                    keypoint_text_resp.response_info
                )

                # Use the generated text as the full report
                full_report = (
                    keypoint_text_resp.text
                    + "\n\nReferences:\n"
                    + "\n".join(keypoint_text_resp.references)
                )

                # Still keep the individual key points for backward compatibility
                key_points_content = [kp.content for kp in all_key_points]
            else:
                key_points_content = [
                    f"Potential issue: {s.title}" for s in sources[:3]
                ]
                full_report = None

            sorted_sources = sorted(sources, key=lambda s: s.score, reverse=True)
            recs = [f"Review source: {s.title} ({s.url})" for s in sorted_sources[:2]]

        resp = ExternalContextResponse(
            sector_summary=summary,
            key_points=key_points_content,
            sources=sorted_sources,
            workshop_recommendations=recs,
            full_report=full_report,
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
    graph.add_node("aggregate", aggregate)

    # Set up the graph with parallel processing
    graph.set_entry_point("news")

    # After each search, extract key points from that source type
    graph.add_edge("news", "extract_news_key_points")
    graph.add_edge("extract_news_key_points", "professional")

    graph.add_edge("professional", "extract_professional_key_points")
    graph.add_edge("extract_professional_key_points", "regulatory")

    graph.add_edge("regulatory", "extract_regulatory_key_points")
    graph.add_edge("extract_regulatory_key_points", "aggregate")

    graph.add_edge("aggregate", END)

    return graph.compile()


async def enrich_context(
    request: ExternalContextRequest,
) -> ExternalContextResponse:
    """Run the external context enrichment workflow asynchronously."""

    app = _build_graph(request)
    result = await app.ainvoke({})
    return result["response"]
