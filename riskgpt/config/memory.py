from langchain.memory import ConversationBufferMemory, RedisChatMessageHistory
from pydantic import BaseSettings
from typing import Optional, Literal

class MemorySettings(BaseSettings):
    type: Literal["none", "buffer", "redis"] = "buffer"
    redis_url: Optional[str] = None

def get_memory(settings: MemorySettings = MemorySettings()):
    if settings.type == "none":
        return None
    elif settings.type == "buffer":
        return ConversationBufferMemory(return_messages=True)
    elif settings.type == "redis":
        return RedisChatMessageHistory(url=settings.redis_url)