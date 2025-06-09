from riskgpt.chains.get_mitigations import get_mitigations_chain
from riskgpt.models.schemas import BusinessContext, MitigationRequest


def test_get_mitigations_chain():
    request = MitigationRequest(
        business_context=BusinessContext(
            project_id="123",
            domain_knowledge="Das Unternehmen ist im B2B-Bereich tätig.",
            language="de",
        ),
        risk_description="Ein Systemausfall kann zu Produktionsstopps führen.",
        drivers=["veraltete Hardware"],
    )
    response = get_mitigations_chain(request)
    assert isinstance(response.mitigations, list)
