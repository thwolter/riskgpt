#!/usr/bin/env python
"""
Run Risk Analysis Workflows

This script demonstrates how to run the risk analysis workflows from RiskGPT
including challenge questions, context enrichment, and risk identification
when executed as the main module.
"""

import asyncio
import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

# Import required modules
from riskgpt.chains.challenge_questions import challenge_questions_chain
from riskgpt.logger import configure_logging
from riskgpt.models.chains.questions import ChallengeQuestionsRequest
from riskgpt.models.chains.risk import Risk, RiskRequest
from riskgpt.models.common import BusinessContext
from riskgpt.models.enums import AudienceEnum
from riskgpt.models.workflows.context import EnrichContextRequest
from riskgpt.workflows.enrich_context import enrich_context
from riskgpt.workflows.risk_workflow import risk_workflow

load_dotenv()

# Path to the config file
CONFIG_FILE = Path(__file__).parent / "config.yaml"


def setup_environment():
    """Set up environment variables if not already set."""
    # Check if OPENAI_API_KEY is set, if not prompt for it
    if not os.environ.get("OPENAI_API_KEY"):
        from getpass import getpass

        openai_api_key = getpass("Enter your OpenAI API key: ")
        os.environ["OPENAI_API_KEY"] = openai_api_key

    # Check if TAVILY_API_KEY is set, if not prompt for it
    if not os.environ.get("TAVILY_API_KEY"):
        from getpass import getpass

        tavily_api_key = getpass("Enter your Tavily API key: ")
        os.environ["TAVILY_API_KEY"] = tavily_api_key

    # Set default values for other environment variables if not set
    if not os.environ.get("OPENAI_MODEL_NAME"):
        os.environ["OPENAI_MODEL_NAME"] = "openai:gpt-4.1-nano"

    if not os.environ.get("SEARCH_PROVIDER"):
        os.environ["SEARCH_PROVIDER"] = "tavily"


def create_business_context():
    """Create a business context for the workflows."""
    # Try to load from config file first
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            if "business_context" in config:
                return BusinessContext(**config["business_context"])
        except Exception as e:
            print(f"Error loading business context from config file: {e}")
            print("Falling back to default business context")

    # Fallback to hardcoded values
    return BusinessContext(
        project_id="CLOUD-2023",
        project_description="Migrate on-premises infrastructure to cloud services",
        domain_knowledge="The company is a financial services provider with strict regulatory requirements",
        business_area="IT Infrastructure",
        industry_sector="Financial Services",
    )


def create_existing_risks():
    """Create a list of existing risks for the risk workflow."""
    # Try to load from config file first
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            if "existing_risks" in config:
                return [Risk(**risk) for risk in config["existing_risks"]]
        except Exception as e:
            print(f"Error loading existing risks from config file: {e}")
            print("Falling back to default existing risks")

    # Fallback to hardcoded values
    return [
        Risk(
            title="Data Security Breach",
            description="Risk of unauthorized access to sensitive data during migration",
            category="Security",
        ),
        Risk(
            title="Service Disruption",
            description="Risk of service disruption during the migration process",
            category="Operational",
        ),
    ]


async def run_challenge_questions(context):
    """Run the challenge_questions workflow."""
    # Default values
    audience = AudienceEnum.risk_internal
    focus_areas = ["data security", "compliance", "service continuity"]
    num_questions = 5

    # Try to load from config file
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            if "challenge_questions" in config:
                cq_config = config["challenge_questions"]
                if "audience" in cq_config:
                    audience = getattr(AudienceEnum, cq_config["audience"], audience)
                if "focus_areas" in cq_config:
                    focus_areas = cq_config["focus_areas"]
                if "num_questions" in cq_config:
                    num_questions = cq_config["num_questions"]
        except Exception as e:
            print(f"Error loading challenge questions config: {e}")
            print("Falling back to default challenge questions config")

    # Create a request
    questions_request = ChallengeQuestionsRequest(
        business_context=context,
        audience=audience,
        focus_areas=focus_areas,
        num_questions=num_questions,
    )

    # Run the chain
    response = await challenge_questions_chain(questions_request)
    print(f"Generated {len(response.questions)} challenging questions:")
    for i, question in enumerate(response.questions, 1):
        print(f"{i}. {question}")
    return response


async def run_enrich_context(context):
    """Run the enrich_context workflow."""
    # Default values
    focus_keywords = ["cloud migration", "financial services", "data security"]
    time_horizon_months = 12

    # Try to load from config file
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            if "enrich_context" in config:
                ec_config = config["enrich_context"]
                if "focus_keywords" in ec_config:
                    focus_keywords = ec_config["focus_keywords"]
                if "time_horizon_months" in ec_config:
                    time_horizon_months = ec_config["time_horizon_months"]
        except Exception as e:
            print(f"Error loading enrich context config: {e}")
            print("Falling back to default enrich context config")

    # Create a request
    enrich_request = EnrichContextRequest(
        business_context=context,
        focus_keywords=focus_keywords,
        time_horizon_months=time_horizon_months,
    )

    # Run the workflow
    response = await enrich_context(enrich_request)
    print("Sector Summary:")
    print(response.sector_summary)
    print("\nWorkshop Recommendations:")
    for i, rec in enumerate(response.workshop_recommendations, 1):
        print(f"{i}. {rec}")
    if response.full_report:
        print("\nFull Report:")
        print(
            response.full_report[:500] + "..."
            if len(response.full_report) > 500
            else response.full_report
        )
    return response


async def run_risk_workflow(context):
    """Run the risk workflow."""
    # Default values
    category = "Technical"
    max_risks = 5

    # Try to load from config file
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            if "risk_workflow" in config:
                rw_config = config["risk_workflow"]
                if "category" in rw_config:
                    category = rw_config["category"]
                if "max_risks" in rw_config:
                    max_risks = rw_config["max_risks"]
        except Exception as e:
            print(f"Error loading risk workflow config: {e}")
            print("Falling back to default risk workflow config")

    # Create a request
    risk_request = RiskRequest(
        business_context=context,
        category=category,
        max_risks=max_risks,
        existing_risks=create_existing_risks(),
    )

    # Run the workflow
    response = await risk_workflow(risk_request)
    print(f"Identified {len(response.risks)} risks:")
    for i, risk in enumerate(response.risks, 1):
        print(f"{i}. {risk.title}: {risk.description}")
        if risk.reference:
            print(f"   Reference: {risk.reference}")
    return response


async def main():
    """Main function to run the risk analysis workflows."""
    configure_logging()
    setup_environment()

    context = create_business_context()

    print("\n=== Running Challenge Questions Workflow ===\n")
    challenge_questions_response = await run_challenge_questions(context)
    print(
        f"{challenge_questions_response.response_info.total_cost} USD consumed for challenge questions workflow"
    )

    print("\n=== Running Enrich Context Workflow ===\n")
    enrich_context_response = await run_enrich_context(context)
    print(
        f"{enrich_context_response.response_info.total_cost} USD consumed for enrich context workflow"
    )

    print("\n=== Running Risk Workflow ===\n")
    risk_response = await run_risk_workflow(context)
    print(f"{risk_response.response_info.total_cost} USD consumed for risk workflow")

    print()


if __name__ == "__main__":
    # Use asyncio.run() to execute the async main function
    asyncio.run(main())
