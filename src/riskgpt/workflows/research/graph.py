from langgraph.graph import END, StateGraph

from riskgpt.config.settings import RiskGPTSettings
from riskgpt.models.workflows.context import ResearchRequest

from ...helpers.search import BaseSearchProvider
from ...helpers.search.duckduckgo import DuckDuckGoSearchProvider
from ...helpers.search.google import GoogleSearchProvider
from ...helpers.search.semantic_scholar import SemanticScholarSearchProvider
from ...helpers.search.tavily import TavilySearchProvider
from ...helpers.search.wikipedia import WikipediaSearchProvider
from ...models.enums import ScopeEnum
from .nodes import (
    aggregate,
    create_extract_key_points_node,
    create_search_node,
    start,
    summarize_key_points,
)
from .state import State

settings = RiskGPTSettings()


def get_research_graph(request: ResearchRequest):
    """
    Returns the uncompiled graph for visualization purposes.

    This method can be used in Jupyter notebooks to visualize the graph structure.

    Example:
        ```python
        from IPython.display import Image, display
        from src.workflows.research import get_enrich_context_graph
        from src.models.workflows.context import ResearchRequest
        from src.models.common import BusinessContext

        # Create a request
        request = ResearchRequest(
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

    # Create nodes and edges only for the scopes specified in the request
    search_nodes = {}
    extract_key_points_nodes = {}

    # For each scope in the request, create the corresponding nodes
    for scope in request.scopes:
        # Create search node for this scope with an appropriate provider from settings
        provider = get_provider(scope)

        search_node = create_search_node(request, scope, provider=provider)
        extract_node = create_extract_key_points_node(
            scope, focus_keywords=request.focus_keywords
        )

        scope_value = scope.value.lower()
        node_name = f"{scope_value}"
        extract_node_name = f"extract_{scope_value}_key_points"

        search_nodes[scope] = node_name
        extract_key_points_nodes[scope] = extract_node_name

        # Add nodes to the graph
        graph.add_node(node_name, search_node)
        graph.add_node(extract_node_name, extract_node)

    # Wrap aggregate to include request
    async def aggregate_node(state: State) -> State:
        return await aggregate(state, request)

    # Add common nodes
    graph.add_node("start", start)
    graph.add_node("aggregate", aggregate_node)
    graph.add_node("summarize_key_points", summarize_key_points)

    # Set up the graph with connections
    graph.set_entry_point("start")

    # Connect start to all search nodes
    for scope, node_name in search_nodes.items():
        graph.add_edge("start", node_name)

        # Connect search to extract key points
        extract_node_name = extract_key_points_nodes[scope]
        graph.add_edge(node_name, extract_node_name)

        # Connect extract key points to summarize
        graph.add_edge(extract_node_name, "summarize_key_points")

    # Final steps
    graph.add_edge("summarize_key_points", "aggregate")
    graph.add_edge("aggregate", END)

    return graph


def get_provider(scope: ScopeEnum) -> BaseSearchProvider:
    scope_value = scope.value.lower()
    provider_name = settings.SCOPE_SEARCH_PROVIDERS.get(
        scope_value, settings.SEARCH_PROVIDER
    )
    # Create the appropriate provider instance
    if provider_name == "semantic_scholar":
        return SemanticScholarSearchProvider()
    elif provider_name == "tavily":
        return TavilySearchProvider()
    elif provider_name == "google":
        return GoogleSearchProvider()
    elif provider_name == "duckduckgo":
        return DuckDuckGoSearchProvider()
    elif provider_name == "wikipedia":
        return WikipediaSearchProvider()
    else:
        raise ValueError(f"Unsupported search provider: {provider_name}")
