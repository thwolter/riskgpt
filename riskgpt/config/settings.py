from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal, Optional


class RiskGPTSettings(BaseSettings):

    model_config = SettingsConfigDict(env_file='../.env', env_ignore_empty=True, extra='ignore')

    MEMORY_TYPE: Literal["none", "buffer", "redis"] = Field(default="buffer")
    REDIS_URL: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    TEMPERATURE: float = Field(default=0.7, ge=0.0, le=1.0)
    OPENAI_MODEL_NAME: str = Field(default="gpt-4.1-mini")
    DEFAULT_PROMPT_VERSION: str = Field(default="v1")

