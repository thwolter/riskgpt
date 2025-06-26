import importlib
import sys
import types

import pytest
from helpers import prompt_loader
from processors.input_validator import (
    validate_assessment_request,
    validate_category_request,
    validate_mitigation_request,
    validate_risk_request,
)


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

    prompt_loader = importlib.reload(
        importlib.import_module("riskgpt.helpers.prompt_loader")
    )
    data = prompt_loader.load_prompt("risk_categories")
    assert data["version"] == "v1"
    assert "{format_instructions}" in data["template"]


def test_load_system_prompt(monkeypatch):
    monkeypatch.setattr(
        prompt_loader, "load_prompt", lambda name, version=None: {"template": "sys"}
    )
    assert prompt_loader.load_system_prompt() == "sys"


def test_load_prompt_default_version(monkeypatch, tmp_path):
    prompts_dir = tmp_path / "prompts" / "foo"
    prompts_dir.mkdir(parents=True)
    file = prompts_dir / "v2.yaml"
    file.write_text('version: "v2"\ndescription: "d"\ntemplate: |\n  test')

    monkeypatch.setattr(prompt_loader, "PROMPT_DIR", tmp_path / "prompts")
    monkeypatch.setenv("DEFAULT_PROMPT_VERSION", "v2")
    importlib.reload(prompt_loader)

    data = prompt_loader.load_prompt("foo")
    assert data["version"] == "v2"


def test_validate_category_request_valid():
    req = {
        "business_context": {
            "project_id": "1",
            "project_description": "Test project",
            "domain_knowledge": "Domain",
            "language": "en",
        }
    }
    result = validate_category_request(req)
    assert result.business_context.project_id == "1"


def test_validate_category_request_invalid():
    req = {"business_context": {}}  # Missing required project_id
    with pytest.raises(ValueError):
        validate_category_request(req)


def test_validate_risk_request_valid():
    req = {
        "business_context": {
            "project_id": "1",
            "project_description": "Test project",
            "language": "en",
        },
        "category": "tech",
    }
    result = validate_risk_request(req)
    assert result.category == "tech"
    assert result.business_context.project_id == "1"


def test_validate_risk_request_invalid():
    with pytest.raises(ValueError):
        validate_risk_request(
            {"business_context": {"project_id": "1"}}
        )  # Missing category


def test_validate_mitigation_request_valid():
    req = {
        "business_context": {
            "project_id": "1",
        },
        "risk": {"title": "Risk Title", "description": "failure"},
        "risk_drivers": [
            {"driver": "x", "explanation": "explanation", "influences": "both"}
        ],
    }
    result = validate_mitigation_request(req)
    assert result.risk.description == "failure"
    assert result.business_context.project_id == "1"


def test_validate_mitigation_request_invalid():
    with pytest.raises(ValueError):
        validate_mitigation_request(
            {"business_context": {"project_id": "1"}}
        )  # Missing risk_description


def test_validate_assessment_request_valid():
    req = {
        "business_context": {
            "project_id": "1",
        },
        "risk_title": "Risk Title",
        "risk_description": "something",
    }
    result = validate_assessment_request(req)
    assert result.business_context.project_id == "1"
    assert result.risk_title == "Risk Title"
    assert result.risk_description == "something"


def test_validate_assessment_request_invalid():
    with pytest.raises(ValueError):
        validate_assessment_request(
            {"risk_description": "foo"}
        )  # Missing business_context
