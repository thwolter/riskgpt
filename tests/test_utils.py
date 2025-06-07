import sys
import importlib
import types
import pytest

pytest.importorskip("pydantic")
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
    data = prompt_loader.load_prompt("get_categories")
    assert data["version"] == "v1"
    assert "You are a risk analyst." in data["template"]


def test_load_prompt_default_version(monkeypatch, tmp_path):
    prompts_dir = tmp_path / "prompts" / "foo"
    prompts_dir.mkdir(parents=True)
    file = prompts_dir / "v2.yaml"
    file.write_text('version: "v2"\ndescription: "d"\ntemplate: |\n  test')

    import importlib
    from riskgpt.utils import prompt_loader

    monkeypatch.setattr(prompt_loader, "PROMPT_DIR", tmp_path / "prompts")
    monkeypatch.setenv("DEFAULT_PROMPT_VERSION", "v2")
    importlib.reload(prompt_loader)

    data = prompt_loader.load_prompt("foo")
    assert data["version"] == "v2"


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

