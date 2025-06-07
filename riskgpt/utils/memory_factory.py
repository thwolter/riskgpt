from langchain.memory.buffer import ConversationBufferMemory
from typing import Optional
from riskgpt.config.settings import RiskGPTSettings

def get_memory(settings: RiskGPTSettings = RiskGPTSettings()) -> Optional[object]:
    if settings.MEMORY_TYPE == "none":
        return None
    elif settings.MEMORY_TYPE == "buffer":
        return ConversationBufferMemory(return_messages=True)
    elif settings.MEMORY_TYPE == "redis":
        raise ValueError("Unsupported memory type: redis. Please configure Redis memory support.")
    return None