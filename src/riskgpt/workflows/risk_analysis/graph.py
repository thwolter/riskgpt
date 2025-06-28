from langgraph.graph import END, StateGraph

from riskgpt.models.enums import TopicEnum
from riskgpt.models.workflows.risk_analysis import RiskAnalysisRequest

from ...helpers.search.semantic_scholar import SemanticScholarSearchProvider
from .nodes import (
    aggregate_risk_analysis,
    create_extract_key_points_node,
    create_search_node,
    start,
    summarize_key_points,
)
from .state import RiskAnalysisState


def get_risk_analysis_graph(request: RiskAnalysisRequest):
    """Returns the uncompiled graph for the risk analysis workflow."""
    graph = StateGraph(RiskAnalysisState)

    # Create node instances
    news_search = create_search_node(request, TopicEnum.NEWS)
    professional_search = create_search_node(request, TopicEnum.LINKEDIN)
    regulatory_search = create_search_node(request, TopicEnum.REGULATORY)
    academic_search = create_search_node(
        request, TopicEnum.ACADEMIC, provider=SemanticScholarSearchProvider()
    )


    extract_news_key_points = create_extract_key_points_node(
        TopicEnum.NEWS, focus_keywords=request.focus_keywords
    )
    extract_professional_key_points = create_extract_key_points_node(
        TopicEnum.LINKEDIN, focus_keywords=request.focus_keywords
    )
    extract_regulatory_key_points = create_extract_key_points_node(
        TopicEnum.REGULATORY, focus_keywords=request.focus_keywords
    )
    extract_academic_key_points = create_extract_key_points_node(
        TopicEnum.ACADEMIC, focus_keywords=request.focus_keywords
    )


    # Wrap aggregate to include request
    async def aggregate_node(state: RiskAnalysisState) -> RiskAnalysisState:
        return await aggregate_risk_analysis(state, request)

    # Add nodes to the graph
    graph.add_node("start", start)
    graph.add_node("news", news_search)
    graph.add_node("professional", professional_search)
    graph.add_node("regulatory", regulatory_search)
    graph.add_node("academic", academic_search)
    graph.add_node("extract_news_key_points", extract_news_key_points)
    graph.add_node("extract_professional_key_points", extract_professional_key_points)
    graph.add_node("extract_regulatory_key_points", extract_regulatory_key_points)
    graph.add_node("extract_academic_key_points", extract_academic_key_points)
    graph.add_node("aggregate", aggregate_node)
    graph.add_node("summarize_key_points", summarize_key_points)

    # Set up the graph with connections
    graph.set_entry_point("start")

    # Branch from start to all search operations
    graph.add_edge("start", "news")
    graph.add_edge("start", "professional")
    graph.add_edge("start", "regulatory")
    graph.add_edge("start", "academic")

    # After each search, extract key points from that source type
    graph.add_edge("news", "extract_news_key_points")
    graph.add_edge("professional", "extract_professional_key_points")
    graph.add_edge("regulatory", "extract_regulatory_key_points")
    graph.add_edge("academic", "extract_academic_key_points")

    # Join all extraction results to summarize key points
    graph.add_edge("extract_news_key_points", "summarize_key_points")
    graph.add_edge("extract_professional_key_points", "summarize_key_points")
    graph.add_edge("extract_regulatory_key_points", "summarize_key_points")
    graph.add_edge("extract_academic_key_points", "summarize_key_points")

    # Final steps
    graph.add_edge("summarize_key_points", "aggregate")
    graph.add_edge("aggregate", END)

    return graph
