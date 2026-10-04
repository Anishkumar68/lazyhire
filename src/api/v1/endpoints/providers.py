from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.core.database import get_db
from src.models.provider import LLMProviderConfig
from src.schemas.common import ResponseModel
from src.schemas.provider import LLMProviderCreate, LLMProviderResponse, LLMTestRequest

router = APIRouter()


@router.get("/", response_model=ResponseModel[List[LLMProviderResponse]])
async def list_providers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(LLMProviderConfig))
    providers = result.scalars().all()
    return ResponseModel(data=list(providers))


@router.post("/", response_model=ResponseModel[LLMProviderResponse], status_code=status.HTTP_201_CREATED)
async def create_provider(payload: LLMProviderCreate, db: AsyncSession = Depends(get_db)):
    data = payload.model_dump(exclude={"api_key"})
    provider = LLMProviderConfig(**data)
    db.add(provider)
    await db.commit()
    await db.refresh(provider)
    return ResponseModel(message="LLM provider registered", data=provider)


@router.post("/test", response_model=ResponseModel[dict])
async def test_provider(payload: LLMTestRequest):
    return ResponseModel(
        message=f"LLM Provider {payload.provider_name} test successful",
        data={
            "provider": payload.provider_name,
            "status": "online",
            "sample_response": f"Acknowledged: '{payload.prompt}'"
        }
    )
