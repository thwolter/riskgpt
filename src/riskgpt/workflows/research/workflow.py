from riskgpt.models.workflows.context import ResearchRequest, ResearchResponse

from .graph import get_research_graph


def _build_graph(request: ResearchRequest):
    return get_research_graph(request).compile()


async def research(
    request: ResearchRequest,
) -> ResearchResponse:
    """Run the external context enrichment workflow asynchronously."""
    app = _build_graph(request)
    result = await app.ainvoke({})
    return result["response"]
