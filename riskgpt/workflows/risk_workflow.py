"""Workflow for risk identification and assessment with document integration."""

from __future__ import annotations

from typing import Any, Dict

from langchain_core.output_parsers import PydanticOutputParser

from riskgpt.api import fetch_documents, search_context
from riskgpt.chains import get_assessment_chain
from riskgpt.chains.base import BaseChain
from riskgpt.config.settings import RiskGPTSettings
from riskgpt.logger import logger
from riskgpt.models.schemas import (
    AssessmentRequest,
    ResponseInfo,
    RiskRequest,
    RiskResponse,
)
from riskgpt.utils.prompt_loader import load_prompt, load_system_prompt

# Import LangGraph components
END: Any
StateGraph: Any
try:
    from langgraph.graph import END as _END
    from langgraph.graph import StateGraph as _StateGraph

    END = _END
    StateGraph = _StateGraph
except Exception:  # pragma: no cover - optional dependency
    END = None
    StateGraph = None


def _identify_risks_directly(request: RiskRequest) -> RiskResponse:
    """
    Direct implementation of risk identification without using get_risks_chain.

    This avoids the circular dependency where get_risks_chain suggests using risk_workflow.
    """
    settings = RiskGPTSettings()
    prompt_data = load_prompt("get_risks")
    system_prompt = load_system_prompt()

    parser = PydanticOutputParser(pydantic_object=RiskResponse)
    chain = BaseChain(
        prompt_template=prompt_data["template"],
        parser=parser,
        settings=settings,
        prompt_name="get_risks",
    )

    inputs = request.model_dump()
    # Extract fields from business_context and add them directly to inputs
    inputs["project_description"] = request.business_context.project_description
    inputs["language"] = request.business_context.language

    inputs["domain_section"] = (
        f"Domain knowledge: {request.business_context.domain_knowledge}"
        if request.business_context.domain_knowledge
        else ""
    )
    inputs["existing_risks_section"] = (
        f"Existing risks: {', '.join(request.existing_risks)}"
        if request.existing_risks
        else ""
    )
    inputs["system_prompt"] = system_prompt

    return chain.invoke(inputs)


def _build_risk_workflow_graph(request: RiskRequest, use_full_workflow: bool = True):
    """
    Build and compile the risk workflow graph.

    Args:
        request: The risk request containing business context and category
        use_full_workflow: Whether to use the full workflow capabilities (search, document integration)
                          or a simpler version similar to the legacy chains
    """
    if StateGraph is None:
        raise ImportError("langgraph is required for this workflow")

    graph = StateGraph(Dict[str, Any])

    settings = RiskGPTSettings()
    totals: Dict[str, float | int] = {"tokens": 0, "cost": 0.0}

    def initialize_state(state: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize the state with the request if it exists in the input."""
        if "request" in state and isinstance(state["request"], RiskRequest):
            # Use the request from the input state
            pass
        else:
            # Use the request passed to _build_graph
            state["request"] = request

        # Store whether we're using the full workflow
        state["use_full_workflow"] = use_full_workflow
        return state

    def search_for_context(state: Dict[str, Any]) -> Dict[str, Any]:
        """Search for relevant context using the search provider."""
        if not state.get("use_full_workflow", True):
            # Skip this step if not using full workflow
            return state

        req = state["request"]
        logger.info("Searching for context related to '%s'", req.category)

        # Build search query from business context and category
        query = f"{req.business_context.project_description or req.business_context.project_id} {req.business_context.domain_knowledge or ''} {req.category} risks"

        # Perform search
        search_results, success = search_context(query, "risk_context")
        if success and search_results:
            state["search_results"] = search_results
            logger.info("Found %d search results", len(search_results))

            # Extract references from search results
            references = [result.get("title", "") for result in search_results]
            state["references"] = references
        else:
            logger.warning("Search failed or returned no results")
            state["search_results"] = []
            state["references"] = []

        return state

    def fetch_documents_step(state: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch relevant documents for the business context."""
        if not state.get("use_full_workflow", True):
            # Skip this step if not using full workflow
            return state

        req = state["request"]
        logger.info(
            "Fetching documents for project '%s'", req.business_context.project_id
        )

        # Call the API helper that integrates with the document service
        document_refs = fetch_documents(req.business_context)
        state["document_refs"] = document_refs

        logger.info("Found %d relevant documents", len(document_refs))
        return state

    def identify_risks(state: Dict[str, Any]) -> Dict[str, Any]:
        """Identify risks using direct implementation to avoid circular dependency."""
        req = state["request"]
        logger.info("Identify risks for category '%s'", req.category)

        # Create a copy of the request with document_refs if available
        risk_request = RiskRequest(
            business_context=req.business_context,
            category=req.category,
            max_risks=req.max_risks,
            existing_risks=req.existing_risks,
        )

        # If we have document_refs in the state, add them to the request
        if "document_refs" in state and state["document_refs"]:
            risk_request.document_refs = state["document_refs"]

        # Use direct implementation instead of get_risks_chain to avoid circular dependency
        res = _identify_risks_directly(risk_request)

        if res.response_info:
            totals["tokens"] += res.response_info.consumed_tokens
            totals["cost"] += res.response_info.total_cost

        # Add search references if they exist in the state
        if "references" in state and state["references"]:
            res.references = state["references"]

        # Add document_refs if they exist in the state
        if (
            "document_refs" in state
            and state["document_refs"]
            and not hasattr(res, "document_refs")
        ):
            res.document_refs = state["document_refs"]

        state["risks"] = res.risks
        state["risk_response"] = res
        return state

    def assess_risks(state: Dict[str, Any]) -> Dict[str, Any]:
        """Assess each identified risk using the get_assessment_chain."""
        if not state.get("use_full_workflow", True):
            # Skip risk assessment if not using full workflow
            # Just return the state with the identified risks
            return state

        req = state["request"]
        assessments = []

        for risk in state.get("risks", []):
            logger.info("Assess risk '%s'", risk.title)

            # Create assessment request
            assessment_request = AssessmentRequest(
                business_context=req.business_context,
                risk_description=risk.description,
            )

            # If we have document_refs in the state, add them to the request
            if "document_refs" in state and state["document_refs"]:
                assessment_request.document_refs = state["document_refs"]

            # If we have references in the state, add them to the request context
            if "references" in state and state["references"]:
                # We can't directly add references to the request, but we can enhance the context
                additional_context = (
                    f"\nRelevant references: {', '.join(state['references'])}"
                )
                assessment_request.risk_description += additional_context

            assess = get_assessment_chain(assessment_request)

            if assess.response_info:
                totals["tokens"] += assess.response_info.consumed_tokens
                totals["cost"] += assess.response_info.total_cost

            # Add document_refs to the response if they exist in the state
            if (
                "document_refs" in state
                and state["document_refs"]
                and not hasattr(assess, "document_refs")
            ):
                assess.document_refs = state["document_refs"]

            assessments.append(assess)

        state["assessments"] = assessments
        return state

    def prepare_response(state: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare the final response."""
        risk_response = state.get("risk_response")

        # Create a new response with the same risks
        # Check if risk_response is None before accessing its attributes
        if risk_response is None:
            # If risk_response is None, create a response with empty lists
            response = RiskResponse(
                risks=[],
                references=[],
            )
        else:
            response = RiskResponse(
                risks=risk_response.risks,
                references=risk_response.references,
            )

        # Add document_refs if they exist in the state
        if "document_refs" in state and state["document_refs"]:
            response.document_refs = state["document_refs"]

        # Add response info
        response.response_info = ResponseInfo(
            consumed_tokens=int(totals["tokens"]),
            total_cost=float(totals["cost"]),
            prompt_name="risk_workflow",
            model_name=settings.OPENAI_MODEL_NAME,
        )

        state["response"] = response
        return state

    # Add nodes to the graph
    graph.add_node("initialize", initialize_state)
    graph.add_node("search_for_context", search_for_context)
    graph.add_node("fetch_documents", fetch_documents_step)
    graph.add_node("identify_risks", identify_risks)
    graph.add_node("assess_risks", assess_risks)
    graph.add_node("prepare_response", prepare_response)

    # Set the entry point
    graph.set_entry_point("initialize")

    # Add edges to define the flow
    if use_full_workflow:
        # Full workflow with search and document integration
        graph.add_edge("initialize", "search_for_context")
        graph.add_edge("search_for_context", "fetch_documents")
        graph.add_edge("fetch_documents", "identify_risks")
        graph.add_edge("identify_risks", "assess_risks")
        graph.add_edge("assess_risks", "prepare_response")
    else:
        # Simple workflow similar to legacy chains
        graph.add_edge("initialize", "identify_risks")
        graph.add_edge("identify_risks", "prepare_response")

    graph.add_edge("prepare_response", END)

    return graph.compile()


def risk_workflow(request: RiskRequest, use_full_workflow: bool = True) -> RiskResponse:
    """
    Run the risk workflow and return a structured response.

    This workflow orchestrates:
    1. Web search for relevant context (if use_full_workflow=True)
    2. Document retrieval from the document microservice (if use_full_workflow=True)
    3. Risk identification (using direct implementation to avoid circular dependency)
    4. Risk assessment (if use_full_workflow=True)

    Args:
        request: The risk request containing business context and category
        use_full_workflow: Whether to use the full workflow capabilities (search, document integration)
                          or a simpler version similar to the legacy chains. Default is True.

    Returns:
        A risk response containing identified risks and document references
    """
    app = _build_risk_workflow_graph(request, use_full_workflow)
    result = app.invoke({"request": request})
    return result["response"]


async def async_risk_workflow(
    request: RiskRequest, use_full_workflow: bool = True
) -> RiskResponse:
    """
    Asynchronous version of the risk workflow.

    Args:
        request: The risk request containing business context and category
        use_full_workflow: Whether to use the full workflow capabilities (search, document integration)
                          or a simpler version similar to the legacy chains. Default is True.

    Returns:
        A risk response containing identified risks and document references
    """
    app = _build_risk_workflow_graph(request, use_full_workflow)
    result = await app.ainvoke({"request": request})
    return result["response"]
