import pytest

pytest.importorskip("langchain")
pytest.importorskip("langchain_openai")
pytest.importorskip("langchain_community")

from riskgpt.chains.get_mitigations import get_mitigations_chain
from riskgpt.models.schemas import MitigationRequest


def test_get_mitigations_chain():
    request = MitigationRequest(
        project_id="123",
        risk_description="Ein Systemausfall kann zu Produktionsstopps führen.",
        drivers=["veraltete Hardware"],
        domain_knowledge="Das Unternehmen ist im B2B-Bereich tätig.",
        language="de",
    )
    response = get_mitigations_chain(request)
    assert isinstance(response.mitigations, list)
