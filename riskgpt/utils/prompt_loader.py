import yaml
from pathlib import Path
from typing import Any, Dict, Optional

from riskgpt.config.settings import RiskGPTSettings
from riskgpt.models.schemas import Prompt


PROMPT_DIR = Path(__file__).parent.parent / "prompts"


def load_prompt(name: str, version: Optional[str] = None) -> Dict[str, Any]:
    if version is None:
        settings = RiskGPTSettings()
        version = settings.DEFAULT_PROMPT_VERSION

    path = PROMPT_DIR / name / f"{version}.yaml"
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    prompt = Prompt(**data)
    return prompt.model_dump()

