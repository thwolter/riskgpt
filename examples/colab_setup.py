"""
RiskGPT Colab Setup Script

This script can be used to quickly set up RiskGPT in Google Colab.
Usage in Colab:
    !curl -s https://raw.githubusercontent.com/thwolter/riskgpt/main/examples/colab_setup.py | python3
"""

import importlib.util
import os
import subprocess
import sys
from getpass import getpass


def check_python_version():
    """Check if Python version is 3.12 or higher."""
    if sys.version_info < (3, 12):
        print("Installing Python 3.12 (required for RiskGPT)...")
        subprocess.run(["apt-get", "update"], check=True)
        subprocess.run(
            [
                "apt-get",
                "install",
                "python3.12",
                "python3.12-dev",
                "python3.12-distutils",
                "-y",
            ],
            check=True,
        )
        subprocess.run(
            [
                "update-alternatives",
                "--install",
                "/usr/bin/python3",
                "python3",
                "/usr/bin/python3.12",
                "1",
            ],
            check=True,
        )
        print(
            "Python 3.12 installed. Please restart the runtime and run this script again."
        )
        print(
            "To restart the runtime, click on 'Runtime' -> 'Restart runtime' in the Colab menu."
        )
        sys.exit(0)
    else:
        print(
            f"Python version {sys.version_info.major}.{sys.version_info.minor} is compatible."
        )


def install_riskgpt():
    """Install RiskGPT from GitHub."""
    print("Installing RiskGPT from GitHub...")
    subprocess.run(
        ["pip", "install", "git+https://github.com/thwolter/riskgpt.git"],
        check=True,
    )
    print("RiskGPT installed successfully.")

    # Note: Alternative installation method
    # If you have access to the wheel file, you can install it with:
    # pip install /path/to/dist/riskgpt-0.1.0-py3-none-any.whl


def setup_api_key():
    """Set up the OpenAI API key."""
    print("\nSetting up OpenAI API key...")
    openai_api_key = getpass("Enter your OpenAI API key: ")
    os.environ["OPENAI_API_KEY"] = openai_api_key
    print("API key set in environment variable.")

    save_key = input(
        "Would you like to save the API key for this session? (y/n): "
    ).lower()
    if save_key == "y":
        with open("/content/openai_key.py", "w") as f:
            f.write(f"import os\nos.environ['OPENAI_API_KEY'] = '{openai_api_key}'\n")
        print("API key saved to /content/openai_key.py")
        print("To load the key in future cells, use: %run /content/openai_key.py")


def print_usage_example():
    """Print a usage example."""
    print("\n" + "=" * 50)
    print("RiskGPT is now ready to use!")
    print("=" * 50)
    print("\nBasic usage example:")
    print("""
from riskgpt import configure_logging
from riskgpt.models.common import BusinessContext
from riskgpt.workflows.risk_workflow import run_risk_workflow

# Configure logging
configure_logging()

# Create a business context
context = BusinessContext(
    project_id="ACME-1",
    project_name="ACME Corp Security Upgrade",
    description="Implement new cybersecurity measures across all departments"
)

# Run the risk workflow
result = run_risk_workflow(context)

# Display the results
print(f"Identified Risks: {len(result.risks)}")
for risk in result.risks:
    print(f"Risk: {risk.title}")
    """)
    print(
        "\nFor more examples and documentation, visit: https://thwolter.github.io/riskgpt/"
    )


def main():
    """Main function to set up RiskGPT in Colab."""
    print("Setting up RiskGPT in Google Colab...\n")

    # Check if running in Colab
    is_colab = importlib.util.find_spec("google.colab") is not None

    if not is_colab:
        print(
            "Warning: This script is designed for Google Colab. Some features may not work correctly."
        )

    check_python_version()
    install_riskgpt()
    setup_api_key()
    print_usage_example()


if __name__ == "__main__":
    main()
