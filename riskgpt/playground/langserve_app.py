"""LangServe playground for RiskGPT.

Run ``python -m riskgpt.playground.langserve_app`` after installing
``riskgpt[serve]`` to launch a local web UI exposing several chains.
"""

from __future__ import annotations

try:
    from fastapi import FastAPI
    from langchain_core.runnables import RunnableLambda
    from langserve import add_routes
except Exception as exc:  # pragma: no cover - optional dependency
    raise SystemExit("LangServe and FastAPI are required for the playground.") from exc

from riskgpt.chains import get_categories_chain, get_risks_chain
from riskgpt.models.schemas import (
    CategoryRequest,
    ContextQualityRequest,
    PresentationRequest,
    RiskRequest,
)
from riskgpt.workflows import check_context_quality, prepare_presentation_output

app = FastAPI(title="RiskGPT Playground")


def custom_openapi() -> dict:
    """Generate OpenAPI schema without batch endpoints."""
    from fastapi.openapi.utils import get_openapi

    filtered_routes = [r for r in app.router.routes if "/batch" not in r.path]
    return get_openapi(title=app.title, version="1.0.0", routes=filtered_routes)


app.openapi = custom_openapi

add_routes(
    app,
    RunnableLambda(lambda data: get_categories_chain(CategoryRequest(**data))),
    path="/get_categories",
    input_type=CategoryRequest,
    disabled_endpoints=["batch"],
)

add_routes(
    app,
    RunnableLambda(lambda data: get_risks_chain(RiskRequest(**data))),
    path="/get_risks",
    input_type=RiskRequest,
    disabled_endpoints=["batch"],
)

add_routes(
    app,
    RunnableLambda(lambda data: check_context_quality(ContextQualityRequest(**data))),
    path="/check_context_quality",
    input_type=ContextQualityRequest,
    disabled_endpoints=["batch"],
)

add_routes(
    app,
    RunnableLambda(
        lambda data: prepare_presentation_output(PresentationRequest(**data))
    ),
    path="/prepare_presentation_output",
    input_type=PresentationRequest,
    disabled_endpoints=["batch"],
)

if __name__ == "__main__":  # pragma: no cover - manual start
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8020)
