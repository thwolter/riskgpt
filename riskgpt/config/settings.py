from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from pydantic import field_validator


class RiskGPTSettings(BaseSettings):

    model_config = SettingsConfigDict(env_file='../.env', env_ignore_empty=True, extra='ignore')

    MEMORY_TYPE: str = Field(default="buffer")
    REDIS_URL: Optional[str] = None
    OPENAI_API_KEY: Optional[SecretStr] = None
    TEMPERATURE: float = Field(default=0.7, ge=0.0, le=1.0)
    OPENAI_MODEL_NAME: str = Field(default="gpt-4.1-mini")
    DEFAULT_PROMPT_VERSION: str = Field(default="v1")

    @field_validator("MEMORY_TYPE")
    @classmethod
    def validate_memory_type(cls, v: str) -> str:
        from riskgpt.utils.memory_factory import _CREATORS
        allowed = {"none", "buffer", "redis"}.union(_CREATORS.keys())
        if v not in allowed:
            raise ValueError("Input should be 'none', 'buffer' or 'redis'")
        return v

