from pydantic import ValidationError

from src.riskgpt.models.chains.assessment import AssessmentRequest
from src.riskgpt.models.chains.categorization import CategoryRequest
from src.riskgpt.models.chains import MitigationRequest
from src.riskgpt.models.chains import RiskRequest


def validate_category_request(data: dict) -> CategoryRequest:
    try:
        return CategoryRequest(**data)
    except ValidationError as e:
        raise ValueError(f"Invalid input data: {e}")


def validate_risk_request(data: dict) -> RiskRequest:
    """Validate dict input and return a :class:`RiskRequest` instance."""
    try:
        return RiskRequest(**data)
    except ValidationError as e:
        raise ValueError(f"Invalid input data: {e}")


def validate_mitigation_request(data: dict) -> MitigationRequest:
    """Validate dict input and return a :class:`MitigationRequest` instance."""
    try:
        return MitigationRequest(**data)
    except ValidationError as e:
        raise ValueError(f"Invalid input data: {e}")


def validate_assessment_request(data: dict) -> AssessmentRequest:
    """Validate dict input and return a :class:`AssessmentRequest` instance."""
    try:
        return AssessmentRequest(**data)
    except ValidationError as e:
        raise ValueError(f"Invalid input data: {e}")
