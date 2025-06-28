from riskgpt.models.workflows.risk_analysis import RiskAnalysisRequest, RiskAnalysisResponse

from .graph import get_risk_analysis_graph


def _build_graph(request: RiskAnalysisRequest):
    return get_risk_analysis_graph(request).compile()


async def analyse_risk(
    request: RiskAnalysisRequest,
) -> RiskAnalysisResponse:
    """Run the risk analysis workflow asynchronously.
    
    This workflow takes a risk and conducts similar steps as enrich_context,
    but focuses on analyzing the risk. It searches for information related to the risk,
    extracts key points, and generates a summary with risk factors, mitigation strategies,
    and impact assessment.
    
    Args:
        request: The risk analysis request containing the risk to analyze
        
    Returns:
        A RiskAnalysisResponse containing the analysis results
    """
    app = _build_graph(request)
    result = await app.ainvoke({})
    return result["response"]