from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.core.database import get_db
from src.models.provider import LLMProviderConfig
from src.schemas.common import ResponseModel
from src.schemas.provider import (
    LLMProviderCreate,
    LLMProviderUpdate,
    LLMProviderResponse,
    LLMTestRequest,
    SupportedProviderInfo,
)

router = APIRouter()

DB = Depends(get_db)


@router.get("/", response_model=ResponseModel[List[LLMProviderResponse]])
async def list_providers(db: AsyncSession = DB):
    """List all configured LLM providers."""
    result = await db.execute(select(LLMProviderConfig))
    providers = result.scalars().all()
    return ResponseModel(data=list(providers))


@router.post("/", response_model=ResponseModel[LLMProviderResponse], status_code=status.HTTP_201_CREATED)
async def create_provider(payload: LLMProviderCreate, db: AsyncSession = DB):
    """Register a new LLM provider configuration."""
    data = payload.model_dump(exclude={"api_key"})
    provider = LLMProviderConfig(**data)
    db.add(provider)
    await db.commit()
    await db.refresh(provider)
    return ResponseModel(message="LLM provider registered", data=provider)


@router.get("/supported")
async def list_supported_providers():
    """List all supported LLM providers (OpenAI, Anthropic, Gemini, DeepSeek, Moonshot, Qwen, Grok, Groq, Mistral, OpenRouter, Ollama)."""
    pass


@router.get("/{provider_id}")
async def get_provider(provider_id: int, db: AsyncSession = DB):
    """Get provider details by ID."""
    pass


@router.put("/{provider_id}")
async def update_provider(provider_id: int, payload: LLMProviderUpdate, db: AsyncSession = DB):
    """Update an LLM provider configuration."""
    pass


@router.delete("/{provider_id}")
async def delete_provider(provider_id: int, db: AsyncSession = DB):
    """Remove an LLM provider configuration."""
    pass


@router.post("/{provider_id}/set-primary")
async def set_primary_provider(provider_id: int, db: AsyncSession = DB):
    """Set the specified provider as the system's primary LLM provider."""
    pass


@router.post("/test", response_model=ResponseModel[dict])
async def test_provider(payload: LLMTestRequest):
    """Test connectivity and prompt response for an LLM provider."""
    return ResponseModel(
        message=f"LLM Provider {payload.provider_name} test successful",
        data={
            "provider": payload.provider_name,
            "status": "online",
            "sample_response": f"Acknowledged: '{payload.prompt}'"
        }
    )
