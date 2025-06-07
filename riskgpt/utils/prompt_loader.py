import yaml
from pathlib import Path
from typing import Any, Dict


PROMPT_DIR = Path(__file__).parent.parent / "prompts"

def load_prompt(name: str, version: str = "v1") -> Dict[str, Any]:
    path = PROMPT_DIR / name / f"{version}.yaml"
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data

