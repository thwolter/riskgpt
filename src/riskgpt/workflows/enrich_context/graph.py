from langgraph.graph import END, StateGraph

from riskgpt.models.enums import TopicEnum
from riskgpt.models.workflows.context import EnrichContextRequest

from .nodes import (
    aggregate,
    create_extract_key_points_node,
    create_search_node,
    start,
    summarize_key_points,
)
from .state import State


def get_enrich_context_graph(request: EnrichContextRequest):
    """
    Returns the uncompiled graph for visualization purposes.

    This method can be used in Jupyter notebooks to visualize the graph structure.

    Example:
        ```python
        from IPython.display import Image, display
        from src.workflows.enrich_context import get_enrich_context_graph
        from src.models.workflows.context import ExternalContextRequest
        from src.models.common import BusinessContext

        # Create a request
        request = ExternalContextRequest(
            business_context=BusinessContext(
                project_id="Sample Project",
                project_description="A sample project for visualization",
                domain_knowledge="sample domain",
            ),
            focus_keywords=["sample", "keywords"],
        )

        # Get the graph
        graph = get_enrich_context_graph(request)

        # Visualize the graph
        try:
            display(Image(graph.get_graph().draw_mermaid_png()))
        except Exception as e:
            print(f"Could not visualize graph: {e}")
            print("Make sure you have graphviz installed.")
        ```
    """
    graph = StateGraph(State)

    # Create node instances
    news_search = create_search_node(request, TopicEnum.NEWS)
    professional_search = create_search_node(request, TopicEnum.LINKEDIN)
    regulatory_search = create_search_node(request, TopicEnum.REGULATORY)

    extract_news_key_points = create_extract_key_points_node(TopicEnum.NEWS)
    extract_professional_key_points = create_extract_key_points_node(TopicEnum.LINKEDIN)
    extract_regulatory_key_points = create_extract_key_points_node(TopicEnum.REGULATORY)

    # Wrap aggregate to include request
    async def aggregate_node(state: State) -> State:
        return await aggregate(state, request)

    # Add nodes to the graph
    graph.add_node("start", start)
    graph.add_node("news", news_search)
    graph.add_node("professional", professional_search)
    graph.add_node("regulatory", regulatory_search)
    graph.add_node("extract_news_key_points", extract_news_key_points)
    graph.add_node("extract_professional_key_points", extract_professional_key_points)
    graph.add_node("extract_regulatory_key_points", extract_regulatory_key_points)
    graph.add_node("aggregate", aggregate_node)
    graph.add_node("summarize_key_points", summarize_key_points)

    # Set up the graph with connections
    graph.set_entry_point("start")

    # Branch from start to all three search operations
    graph.add_edge("start", "news")
    graph.add_edge("start", "professional")
    graph.add_edge("start", "regulatory")

    # After each search, extract key points from that source type
    graph.add_edge("news", "extract_news_key_points")
    graph.add_edge("professional", "extract_professional_key_points")
    graph.add_edge("regulatory", "extract_regulatory_key_points")

    # Join all extraction results to summarize key points
    graph.add_edge("extract_news_key_points", "summarize_key_points")
    graph.add_edge("extract_professional_key_points", "summarize_key_points")
    graph.add_edge("extract_regulatory_key_points", "summarize_key_points")

    # Final steps
    graph.add_edge("summarize_key_points", "aggregate")
    graph.add_edge("aggregate", END)

    return graph
