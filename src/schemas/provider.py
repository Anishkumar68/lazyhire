from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class LLMProviderBase(BaseModel):
    name: str
    is_enabled: bool = True
    is_primary: bool = False
    model_name: str
    base_url: Optional[str] = None
    rate_limit_rpm: int = 60


class LLMProviderCreate(LLMProviderBase):
    api_key: Optional[str] = None


class LLMProviderResponse(LLMProviderBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class LLMTestRequest(BaseModel):
    provider_name: str
    prompt: str = "Hello, respond with 'Provider is working correctly.'"
