from typing import List, Optional

from riskgpt.chains.extract_keypoints import extract_key_points_chain
from riskgpt.chains.keypoints_summary import keypoints_summary_chain
from riskgpt.helpers.search import search
from riskgpt.models.base import ResponseInfo
from riskgpt.models.enums import TopicEnum
from riskgpt.models.helpers.search import SearchResponse, Source
from riskgpt.models.workflows.risk_analysis import (
    RiskAnalysisRequest,
    RiskAnalysisResponse,
)

from ...helpers.search.base import BaseSearchProvider
from ...models.chains.keypoints import (
    ExtractKeyPointsRequest,
    ExtractKeyPointsResponse,
    KeyPointSummaryRequest,
    KeyPointSummaryResponse,
)
from ..enrich_context.deduplicator import KeyPointDeduplicator
from .state import RiskAnalysisState


async def topic_search(
    state: RiskAnalysisState,
    request: RiskAnalysisRequest,
    topic: TopicEnum,
    provider: Optional[BaseSearchProvider] = None,
) -> RiskAnalysisState:
    """Search for information related to the risk in the specified topic."""
    search_request = request.create_search_request(topic)
    search_response: SearchResponse = await search(search_request, provider=provider)

    sources: List[Source] = state.get("sources", [])
    existing_urls = {source.url for source in sources}

    # Convert SearchResult objects to Source objects
    new_sources = [
        Source.from_search_result(item, topic)
        for item in search_response.results
        if item.url not in existing_urls
    ]

    state["sources"] = new_sources

    if not search_response.success:
        state["search_failed"] = True
    return state


async def extract_topic_key_points(
    state: RiskAnalysisState,
    topic: TopicEnum,
    focus_keywords: Optional[List[str]] = None,
) -> RiskAnalysisState:
    """Extract key points from sources of the specified topic."""
    # Filter sources by topic
    sources: List[Source] = state.get("sources", [])
    topic_sources = [source for source in sources if source.topic == topic]

    for source in topic_sources:
        request = ExtractKeyPointsRequest.from_source(
            source, focus_keywords=focus_keywords
        )
        response: ExtractKeyPointsResponse = await extract_key_points_chain(request)

        # Attach source.url to each point in response.points
        for point in response.points:
            point.source_url = source.url

        state.setdefault("response_info_list", []).append(response.response_info)
        state.setdefault("key_points", []).extend(response.points)

    return state


def aggregate_response_info(state):
    """Aggregate response info from all operations."""
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
        prompt_name="risk_analysis",
        model_name=model_name,
    )


# Create node factory functions
def create_search_node(
    request: RiskAnalysisRequest,
    topic: TopicEnum,
    provider: Optional[BaseSearchProvider] = None,
):
    """Create a search node for the specified topic."""

    async def search_node(state: RiskAnalysisState) -> RiskAnalysisState:
        return await topic_search(state, request, topic, provider=provider)

    return search_node


def create_extract_key_points_node(
    topic: TopicEnum, focus_keywords: Optional[List[str]] = None
):
    """Create a node for extracting key points from the specified topic."""

    async def extract_node(state: RiskAnalysisState) -> RiskAnalysisState:
        return await extract_topic_key_points(
            state, topic, focus_keywords=focus_keywords
        )

    return extract_node


async def summarize_key_points(state: RiskAnalysisState) -> RiskAnalysisState:
    """Summarize key points with de-duplication."""
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
                prompt_name="keypoint_text",
                model_name="unknown",
                error=str(e),
            ),
        )
        state["keypoint_text_response"] = fallback_response
        state.setdefault("response_info_list", []).append(
            fallback_response.response_info
        )
    return state


async def aggregate_risk_analysis(
    state: RiskAnalysisState, request: RiskAnalysisRequest
) -> RiskAnalysisState:
    """Aggregate the results into a RiskAnalysisResponse."""

    sources: List[Source] = state.get("sources", [])

    if not sources:
        if state.get("search_failed"):
            risk_summary = "No external data retrieved due to network restrictions or missing dependencies"
        else:
            risk_summary = "No relevant information found for this risk"
        full_report = None
        risk_factors = []
        mitigation_strategies = []
        impact_assessment = "Unable to assess impact due to lack of information"
    else:
        risk_summary = (
            f"Analyzed risk '{request.risk.title}' using {len(sources)} sources."
        )

        kp_text_response = state.get("keypoint_text_response")
        full_report = kp_text_response.format_output() if kp_text_response else None

        # Extract risk factors, mitigation strategies, and impact assessment from key points
        # In a real implementation, these would be derived more intelligently
        key_points = state.get("key_points", [])

        # todo: We need here to call a more sophisticated analysis chain
        risk_factors = [
            f"Risk factor: {point.content[:50]}..."
            for point in key_points[:3]
            if "risk" in point.content.lower()
        ] or ["No specific risk factors identified"]

        mitigation_strategies = [
            f"Strategy: {point.content[:50]}..."
            for point in key_points[:3]
            if "mitigat" in point.content.lower() or "strateg" in point.content.lower()
        ] or ["No specific mitigation strategies identified"]

        impact_assessment = "Medium impact based on available information"

    # Prepare document references
    document_references = (
        request.risk.document_refs if request.risk.document_refs else []
    )

    response = RiskAnalysisResponse(
        risk_summary=risk_summary,
        risk_factors=risk_factors,
        mitigation_strategies=mitigation_strategies,
        impact_assessment=impact_assessment,
        document_references=document_references,
        full_report=full_report,
    )

    # Aggregate response info
    response.response_info = aggregate_response_info(state)

    state["response"] = response
    return state


async def start(state: RiskAnalysisState) -> RiskAnalysisState:
    """Initialize the state."""
    return state
