from riskgpt.models.workflows.context import EnrichContextRequest, EnrichContextResponse

from .graph import get_enrich_context_graph


def _build_graph(request: EnrichContextRequest):
    return get_enrich_context_graph(request).compile()


async def enrich_context(
    request: EnrichContextRequest,
) -> EnrichContextResponse:
    """Run the external context enrichment workflow asynchronously."""
    app = _build_graph(request)
    result = await app.ainvoke({})
    return result["response"]
