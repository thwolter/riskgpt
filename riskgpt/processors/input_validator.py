from pydantic import ValidationError
from riskgpt.models.schemas import CategoryRequest

def validate_category_request(data: dict) -> CategoryRequest:
    try:
        return CategoryRequest(**data)
    except ValidationError as e:
        raise ValueError(f"Invalid input data: {e}")