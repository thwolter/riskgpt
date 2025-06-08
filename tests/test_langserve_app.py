import pytest

fastapi = pytest.importorskip("fastapi")  # noqa: E402
langserve = pytest.importorskip("langserve")  # noqa: E402

from fastapi.testclient import TestClient  # noqa: E402

from riskgpt.playground.langserve_app import app  # noqa: E402


def test_langserve_app_invocation():
    client = TestClient(app)
    resp = client.post(
        "/get_categories/invoke",
        json={
            "input": {
                "project_id": "1",
                "project_description": "Test project",
                "domain_knowledge": None,
                "language": "en",
            }
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "output" in data and "categories" in data["output"]
