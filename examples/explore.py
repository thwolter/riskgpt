#!/usr/bin/env python
"""
Run Challenge Questions and Enrich Context Workflows

This script demonstrates how to run the challenge_questions and enrich_context
workflows from RiskGPT when executed as the main module.
"""

import asyncio
import os

from dotenv import load_dotenv

# Import required modules
from riskgpt.chains.challenge_questions import challenge_questions_chain
from riskgpt.logger import configure_logging
from riskgpt.models.chains.questions import (
    ChallengeQuestionsRequest,
)
from riskgpt.models.chains.risk import Risk
from riskgpt.models.common import BusinessContext
from riskgpt.models.enums import AudienceEnum
from riskgpt.models.workflows.context import EnrichContextRequest
from riskgpt.workflows.enrich_context import enrich_context

load_dotenv()


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
    return BusinessContext(
        project_id="CLOUD-2023",
        project_description="Migrate on-premises infrastructure to cloud services",
        domain_knowledge="The company is a financial services provider with strict regulatory requirements",
        business_area="IT Infrastructure",
        industry_sector="Financial Services",
    )


def create_sample_risk():
    """Create a sample risk for the challenge_risk workflow."""
    return Risk(
        title="Data Security Breach",
        description="Risk of unauthorized access to sensitive data during migration",
        category="Security",
    )


async def run_challenge_questions(context):
    """Run the challenge_questions workflow."""
    # Create a request
    questions_request = ChallengeQuestionsRequest(
        business_context=context,
        audience=AudienceEnum.risk_internal,
        focus_areas=["data security", "compliance", "service continuity"],
        num_questions=5,
    )

    # Run the chain
    response = await challenge_questions_chain(questions_request)
    print(f"Generated {len(response.questions)} challenging questions:")
    for i, question in enumerate(response.questions, 1):
        print(f"{i}. {question}")
    return response


async def run_enrich_context(context):
    """Run the enrich_context workflow."""
    # Create a request
    enrich_request = EnrichContextRequest(
        business_context=context,
        focus_keywords=["cloud migration", "financial services", "data security"],
        time_horizon_months=12,
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


async def main():
    """Main function to run the workflows."""
    configure_logging()
    setup_environment()

    context = create_business_context()

    print("\n=== Running Challenge Questions Workflow ===\n")
    challenge_questions_response = await run_challenge_questions(context)
    print(challenge_questions_response.model_dump(mode="json", exclude_none=True))

    print("\n=== Running Enrich Context Workflow ===\n")
    enrich_context_response = await run_enrich_context(context)
    print(enrich_context_response.model_dump(mode="json", exclude_none=True))

    print()


if __name__ == "__main__":
    # Use asyncio.run() to execute the async main function
    asyncio.run(main())
