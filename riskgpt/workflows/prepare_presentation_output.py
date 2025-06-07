from __future__ import annotations

from typing import Any, Dict, List

from riskgpt.logger import logger
from riskgpt.models.schemas import (
    PresentationRequest,
    PresentationResponse,
    RiskRequest,
    AssessmentRequest,
    MitigationRequest,
    DriverRequest,
    CorrelationTagRequest,
    CommunicationRequest,
    ResponseInfo,
    AudienceEnum,
)
from riskgpt.config.settings import RiskGPTSettings
from riskgpt.chains import (
    get_risks_chain,
    get_assessment_chain,
    get_mitigations_chain,
    get_drivers_chain,
    get_correlation_tags_chain,
    communicate_risks_chain,
)


def apply_audience_formatting(resp: PresentationResponse, audience: AudienceEnum) -> PresentationResponse:
    """Adjust output fields based on the target audience."""
    if audience == AudienceEnum.executive:
        resp.main_risks = resp.main_risks[:3]
        resp.chart_placeholders = ["executive_overview_chart"]
        resp.open_questions = None
    elif audience == AudienceEnum.workshop:
        resp.open_questions = ["Discuss mitigation priorities"]
    elif audience == AudienceEnum.risk_internal:
        resp.appendix = (resp.appendix or "") + "\n[Model parameters]"
    elif audience == AudienceEnum.audit:
        resp.appendix = (resp.appendix or "") + "\n[Audit trail]"
    elif audience == AudienceEnum.regulator:
        resp.appendix = (resp.appendix or "") + "\n[Compliance mapping]"
    elif audience == AudienceEnum.project_owner:
        resp.appendix = (resp.appendix or "") + "\n[Project milestones]"
    elif audience == AudienceEnum.investor:
        resp.appendix = (resp.appendix or "") + "\n[Financial impact]"
    elif audience == AudienceEnum.operations:
        resp.appendix = (resp.appendix or "") + "\n[KRI dashboard]"
    return resp

try:
    from langgraph.graph import END, StateGraph
except Exception:  # pragma: no cover - optional dependency
    END = None
    StateGraph = None


def _build_graph(request: PresentationRequest):
    if StateGraph is None:
        raise ImportError("langgraph is required for this workflow")

    graph = StateGraph(Dict[str, Any])

    settings = RiskGPTSettings()
    totals = {"tokens": 0, "cost": 0.0}

    def identify_risks(state: Dict[str, Any]) -> Dict[str, Any]:
        category = (request.focus_areas or ["General"])[0]
        logger.info("Identify risks for category '%s'", category)
        res = get_risks_chain(
            RiskRequest(
                project_id=request.project_id,
                project_description=request.project_description,
                category=category,
                language=request.language,
            )
        )
        if res.response_info:
            totals["tokens"] += res.response_info.consumed_tokens
            totals["cost"] += res.response_info.total_cost
        state["risks"] = res.risks
        return state

    def assess_risks(state: Dict[str, Any]) -> Dict[str, Any]:
        assessments = []
        for risk in state.get("risks", []):
            logger.info("Assess risk '%s'", risk.title)
            assess = get_assessment_chain(
                AssessmentRequest(
                    project_id=request.project_id,
                    risk_description=risk.description,
                    language=request.language,
                )
            )
            if assess.response_info:
                totals["tokens"] += assess.response_info.consumed_tokens
                totals["cost"] += assess.response_info.total_cost
            assessments.append(assess)
        state["assessments"] = assessments
        return state

    def drivers(state: Dict[str, Any]) -> Dict[str, Any]:
        driver_lists: List[List[str]] = []
        for risk in state.get("risks", []):
            logger.info("Get drivers for '%s'", risk.title)
            res = get_drivers_chain(
                DriverRequest(
                    project_id=request.project_id,
                    risk_description=risk.description,
                    language=request.language,
                )
            )
            if res.response_info:
                totals["tokens"] += res.response_info.consumed_tokens
                totals["cost"] += res.response_info.total_cost
            driver_lists.append(res.drivers)
        state["drivers"] = driver_lists
        return state

    def mitigations(state: Dict[str, Any]) -> Dict[str, Any]:
        mitigation_lists: List[List[str]] = []
        for risk, drv in zip(state.get("risks", []), state.get("drivers", [])):
            logger.info("Get mitigations for '%s'", risk.title)
            res = get_mitigations_chain(
                MitigationRequest(
                    project_id=request.project_id,
                    risk_description=risk.description,
                    drivers=drv,
                    language=request.language,
                )
            )
            if res.response_info:
                totals["tokens"] += res.response_info.consumed_tokens
                totals["cost"] += res.response_info.total_cost
            mitigation_lists.append(res.mitigations)
        state["mitigations"] = mitigation_lists
        return state

    def correlation(state: Dict[str, Any]) -> Dict[str, Any]:
        titles = [r.title for r in state.get("risks", [])]
        known = [d for lst in state.get("drivers", []) for d in lst]
        logger.info("Define correlation tags")
        res = get_correlation_tags_chain(
            CorrelationTagRequest(
                project_description=request.project_description,
                risk_titles=titles,
                known_drivers=known or None,
                language=request.language,
            )
        )
        if res.response_info:
            totals["tokens"] += res.response_info.consumed_tokens
            totals["cost"] += res.response_info.total_cost
        state["correlation_tags"] = res.tags
        return state

    def summary(state: Dict[str, Any]) -> Dict[str, Any]:
        lines = []
        for risk, assess in zip(state.get("risks", []), state.get("assessments", [])):
            line = f"{risk.title}: P={assess.probability or 'n/a'}, I={assess.impact or 'n/a'}"
            lines.append(line)
        text = "\n".join(lines)
        com = communicate_risks_chain(
            CommunicationRequest(
                project_id=request.project_id,
                summary=text,
                language=request.language,
            )
        )
        if com.response_info:
            totals["tokens"] += com.response_info.consumed_tokens
            totals["cost"] += com.response_info.total_cost
        resp = PresentationResponse(
            executive_summary=com.executive_summary,
            main_risks=[r.title for r in state.get("risks", [])],
            quantitative_summary=text,
            key_drivers=[d for lst in state.get("drivers", []) for d in lst] or None,
            correlation_tags=state.get("correlation_tags"),
            mitigations=[m for lst in state.get("mitigations", []) for m in lst] or None,
            open_questions=[],
            chart_placeholders=["risk_overview_chart"],
            appendix=com.technical_annex,
        )
        resp.response_info = ResponseInfo(
            consumed_tokens=totals["tokens"],
            total_cost=totals["cost"],
            prompt_name="prepare_presentation_output",
            model_name=settings.OPENAI_MODEL_NAME,
        )
        state["response"] = apply_audience_formatting(resp, request.audience)
        return state

    graph.add_node("identify_risks", identify_risks)
    graph.add_node("assess_risks", assess_risks)
    graph.add_node("drivers", drivers)
    graph.add_node("mitigations", mitigations)
    graph.add_node("correlation", correlation)
    graph.add_node("summary", summary)

    graph.set_entry_point("identify_risks")
    graph.add_edge("identify_risks", "assess_risks")
    graph.add_edge("assess_risks", "drivers")
    graph.add_edge("drivers", "mitigations")
    graph.add_edge("mitigations", "correlation")
    graph.add_edge("correlation", "summary")
    graph.add_edge("summary", END)

    return graph.compile()


def prepare_presentation_output(request: PresentationRequest) -> PresentationResponse:
    """Run the presentation workflow and return a structured response."""

    app = _build_graph(request)
    result = app.invoke({})
    return result["response"]

