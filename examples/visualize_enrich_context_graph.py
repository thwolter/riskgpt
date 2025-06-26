"""
Example script to visualize the enrich_context graph.

This script demonstrates how to use the get_enrich_context_graph function
to visualize the graph structure of the enrich_context workflow.

Requirements:
    - IPython
    - graphviz

To install the required dependencies:
    pip install ipython graphviz
"""

from IPython.display import Image, display
from src.models.common import BusinessContext
from src.models.workflows.context import ExternalContextRequest
from src.workflows.enrich_context import get_enrich_context_graph

# Create a sample request
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
    # For Jupyter notebooks
    display(Image(graph.get_graph().draw_mermaid_png()))
    print("Graph visualization successful!")
except Exception as e:
    print(f"Could not visualize graph: {e}")
    print("Make sure you have graphviz installed.")
    
    # Alternative: Save the graph as a file
    try:
        graph_png = graph.get_graph().draw_mermaid_png()
        with open("enrich_context_graph.png", "wb") as f:
            f.write(graph_png)
        print("Graph saved as 'enrich_context_graph.png'")
    except Exception as e:
        print(f"Could not save graph: {e}")