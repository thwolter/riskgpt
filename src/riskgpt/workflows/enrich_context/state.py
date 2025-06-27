from typing import Annotated, List, TypedDict, TypeVar

from langgraph.graph import add_messages

from riskgpt.models.base import ResponseInfo
from riskgpt.models.chains.keypoints import KeyPoint, KeyPointSummaryResponse
from riskgpt.models.helpers.search import Source
from riskgpt.models.workflows.context import EnrichContextResponse

# Define reducer functions for lists
T = TypeVar("T")


def extend_list(existing: List[T] | None, new: List[T]) -> List[T]:
    """Combine two lists by extending the existing list with the new one."""
    if existing is None:
        return new
    return existing + new


def append_to_list(existing: List[T] | None, new: T) -> List[T]:
    """Append a single item to a list."""
    if existing is None:
        return [new]
    return existing + [new]


def combine_bool_or(existing: bool | None, new: bool) -> bool:
    """Combine two boolean values using logical OR."""
    if existing is None:
        return new
    return existing or new


class State(TypedDict):
    messages: Annotated[list, add_messages]
    sources: Annotated[List[Source], extend_list]
    key_points: Annotated[List[KeyPoint], extend_list]
    response_info_list: Annotated[List[ResponseInfo], extend_list]
    search_failed: Annotated[bool, combine_bool_or]
    keypoint_text_response: KeyPointSummaryResponse
    response: EnrichContextResponse
