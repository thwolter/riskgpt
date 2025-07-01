from typing import List, Optional

from riskgpt.chains.extract_keypoints import extract_key_points_chain
from riskgpt.chains.keypoints_summary import keypoints_summary_chain
from riskgpt.helpers.search import search
from riskgpt.models.base import ResponseInfo
from riskgpt.models.enums import ScopeEnum
from riskgpt.models.helpers.search import SearchResponse, Source
from riskgpt.models.workflows.context import ResearchRequest, ResearchResponse

from ...helpers.search.base import BaseSearchProvider
from ...models.chains.keypoints import (
    ExtractKeyPointsRequest,
    ExtractKeyPointsResponse,
    KeyPointSummaryRequest,
    KeyPointSummaryResponse,
)
from .deduplicator import KeyPointDeduplicator
from .state import State


async def scope_search(
    state: State,
    request: ResearchRequest,
    scope: ScopeEnum,
    provider: Optional[BaseSearchProvider] = None,
) -> State:
    search_request = request.create_search_request(scope)
    search_response: SearchResponse = await search(search_request, provider=provider)

    sources: List[Source] = state.get("sources", [])
    existing_urls = {source.citation.url for source in sources}

    # Convert SearchResult objects to Source objects
    new_sources = [
        Source.from_search_result(item, scope)
        for item in search_response.results
        if item.citation.url not in existing_urls
    ]

    state["sources"] = new_sources

    if not search_response.success:
        state["search_failed"] = True
    return state


async def extract_scope_key_points(
    state: State, scope: ScopeEnum, focus_keywords: Optional[List[str]] = None
) -> State:
    # Filter sources by scope
    sources: List[Source] = state.get("sources", [])
    scope_sources = [source for source in sources if source.scope == scope]

    # Handle empty sources case
    if not scope_sources:
        state["search_failed"] = True
        return state

    for source in scope_sources:
        request = ExtractKeyPointsRequest.from_source(
            source, focus_keywords=focus_keywords
        )
        response: ExtractKeyPointsResponse = await extract_key_points_chain(request)

        # Check for error in response
        if response.response_info and response.response_info.error:
            state["search_failed"] = True
            return state

        # Attach citation to each point in response.points
        for point in response.points:
            # Always ensure point.citation has the source URL
            point.citation.url = source.citation.url

            # If source has a full citation, use it
            if (
                hasattr(source, "citation")
                and source.citation
                and source.citation.title
            ):
                point.citation = source.citation

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


# Create node factory functions
def create_search_node(
    request: ResearchRequest,
    scope: ScopeEnum,
    provider: Optional[BaseSearchProvider] = None,
):
    async def search_node(state: State) -> State:
        return await scope_search(state, request, scope, provider=provider)

    return search_node


def create_extract_key_points_node(
    scope: ScopeEnum, focus_keywords: Optional[List[str]] = None
):
    async def extract_node(state: State) -> State:
        return await extract_scope_key_points(
            state, scope, focus_keywords=focus_keywords
        )

    return extract_node


async def summarize_key_points(state: State) -> State:
    """Summarize key points for a specific topic with de-duplication."""

    key_points = state.get("key_points", [])

    # De-duplicate key points before creating the request
    deduplicator = KeyPointDeduplicator(key_points)
    deduplicated_points = deduplicator.deduplicate()

    kp_text_request = KeyPointSummaryRequest(key_points=deduplicated_points)

    try:
        response: KeyPointSummaryResponse = await keypoints_summary_chain(
            kp_text_request
        )
        state["keypoint_text_response"] = response

        if response.response_info:
            state.setdefault("response_info_list", []).append(response.response_info)
    except Exception as e:
        # Create a fallback response with error information
        fallback_response = KeyPointSummaryResponse(
            text="Unable to generate summary text due to parsing error.",
            references=["Error occurred during text generation."],
            response_info=ResponseInfo(
                consumed_tokens=0,
                total_cost=0.0,
                prompt_name="keypoint_summary",
                model_name="unknown",
                error=str(e),
            ),
        )
        state["keypoint_text_response"] = fallback_response
        state.setdefault("response_info_list", []).append(
            fallback_response.response_info
        )
    return state


async def aggregate(state: State, request: ResearchRequest) -> State:
    sources: List[Source] = state.get("sources", [])

    if not sources:
        if state.get("search_failed"):
            summary = "No external data retrieved due to network restrictions or missing dependencies"
        else:
            summary = "No recent relevant information found"
        full_report = None
        recommendation = None
    else:
        summary = f"Collected {len(sources)} external sources."

        kp_text_response = state.get("keypoint_text_response")
        full_report = kp_text_response.format_output() if kp_text_response else None

        sorted_sources = sorted(sources, key=lambda s: s.score, reverse=True)
        recommendation = [
            f"Review source: {s.citation.title} ({s.citation.url})"
            for s in sorted_sources[:2]
        ]

    response = ResearchResponse(
        summary=summary,
        recommendations=recommendation if recommendation else [],
        full_report=full_report,
    )
    response.response_info = aggregate_response_info(state)

    state["response"] = response
    return state


async def start(state: State) -> State:
    return state
