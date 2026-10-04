from fastapi import APIRouter
from src.schemas.common import ResponseModel
from src.core.config import settings

router = APIRouter()


@router.get("/health", response_model=ResponseModel[dict])
async def health_check():
    return ResponseModel(
        success=True,
        message="LazyHire service is healthy",
        data={
            "app": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "env": settings.ENV,
            "status": "healthy"
        }
    )


@router.get("/ready", response_model=ResponseModel[dict])
async def readiness_check():
    return ResponseModel(
        success=True,
        message="System ready",
        data={"ready": True}
    )
