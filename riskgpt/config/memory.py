"""Configuration helper for memory backends."""

from typing import Literal, Optional

from pydantic_settings import BaseSettings

from riskgpt.config.settings import RiskGPTSettings
from riskgpt.utils.memory_factory import (
    get_memory as factory_get_memory,
)


class MemorySettings(BaseSettings):
    """Settings for memory creation."""

    type: Literal["none", "buffer", "redis"] = "buffer"
    redis_url: Optional[str] = None


def get_memory(settings: MemorySettings = MemorySettings()):
    return factory_get_memory(
        RiskGPTSettings(MEMORY_TYPE=settings.type, REDIS_URL=settings.redis_url)
    )
