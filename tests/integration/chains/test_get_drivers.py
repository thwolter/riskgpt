from unittest.mock import patch

import pytest

from src.chains.get_drivers import get_drivers_chain
from src.models.chains.drivers import DriverRequest, DriverResponse, RiskDriver
from src.models.chains.risk import Risk
from src.models.common import BusinessContext


@pytest.fixture
def test_request():
    """Fixture to create a sample DriverRequest."""
    return DriverRequest(
        business_context=BusinessContext(
            project_id="New machine learning project",
            project_description="This project involves developing a machine learning model to predict customer churn.",
            domain_knowledge="Machine learning, customer analytics",
        ),
        risk=Risk(
            title="Customer churn risk",
            description="There is a 20% chance that the machine learning model will not generalize well to new data, leading to inaccurate predictions.",
        ),
    )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_drivers_chain(test_request):
    response = await get_drivers_chain(test_request)
    assert isinstance(response.drivers, list)
    assert len(response.drivers) > 0


@pytest.mark.asyncio
async def test_get_drivers_chain_with_mock(test_request):
    expected = DriverResponse(
        drivers=[
            RiskDriver(
                driver="Data quality issues",
                explanation="Poor quality of training data can lead to inaccurate model predictions.",
                influences="both",
                reference="https://example.com/data-quality",
            ),
            RiskDriver(
                driver="Model overfitting",
                explanation="The model may perform well on training data but poorly on unseen data.",
                influences="likelihood",
                reference="https://example.com/overfitting",
            ),
        ]
    )

    async def mock_invoke(*args, **kwargs):
        return expected

    with patch("src.chains.base.BaseChain.invoke", side_effect=mock_invoke):
        resp = await get_drivers_chain(test_request)
        assert resp.drivers == expected.drivers
