import sys
import importlib
import types
import pytest
from riskgpt.processors.input_validator import validate_category_request


def test_load_prompt(monkeypatch):
    yaml_stub = types.ModuleType("yaml")

    def safe_load(stream):
        text = stream.read()
        lines = text.splitlines()
        result = {}
        idx = 0
        while idx < len(lines):
            line = lines[idx]
            if line.startswith("version:"):
                result["version"] = line.split(":", 1)[1].strip().strip('"')
            elif line.startswith("description:"):
                result["description"] = line.split(":", 1)[1].strip().strip('"')
            elif line.startswith("template:"):
                idx += 1
                template_lines = []
                while idx < len(lines):
                    template_lines.append(lines[idx].lstrip())
                    idx += 1
                result["template"] = "\n".join(template_lines)
                break
            idx += 1
        return result

    yaml_stub.safe_load = safe_load
    monkeypatch.setitem(sys.modules, "yaml", yaml_stub)

    prompt_loader = importlib.reload(importlib.import_module("riskgpt.utils.prompt_loader"))
    data = prompt_loader.load_prompt("get_categories", "v1")
    assert data["version"] == "v1"
    assert "You are a risk analyst." in data["template"]


def test_validate_category_request_valid():
    req = {
        "project_id": "1",
        "project_description": "Test project",
        "domain_knowledge": "Domain",
        "language": "en",
    }
    result = validate_category_request(req)
    assert result.project_id == "1"
    assert result.language == "en"


def test_validate_category_request_invalid():
    req = {"project_description": "Test project"}
    with pytest.raises(ValueError):
        validate_category_request(req)

