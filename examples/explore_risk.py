#!/usr/bin/env python
"""
Run Risk Workflow

This script demonstrates how to run the risk workflow from RiskGPT
when executed as the main module.
"""

import asyncio
import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

# Import required modules
from riskgpt.logger import configure_logging
from riskgpt.models.chains.risk import Risk, RiskRequest
from riskgpt.models.common import BusinessContext
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
    """Main function to run the workflow."""
    configure_logging()
    setup_environment()

    context = create_business_context()

    print("\n=== Running Risk Workflow ===\n")
    risk_response = await run_risk_workflow(context)
    print(f"{risk_response.response_info.total_cost} USD consumed for risk workflow")

    print()


if __name__ == "__main__":
    # Use asyncio.run() to execute the async main function
    asyncio.run(main())
