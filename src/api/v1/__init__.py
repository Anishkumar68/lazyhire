from fastapi import APIRouter
from src.api.v1.endpoints import health, jobs, profiles, materials, review, applications, providers

api_v1_router = APIRouter()

api_v1_router.include_router(health.router, tags=["Health"])
api_v1_router.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
api_v1_router.include_router(profiles.router, prefix="/profiles", tags=["Profiles"])
api_v1_router.include_router(materials.router, prefix="/materials", tags=["Materials"])
api_v1_router.include_router(review.router, prefix="/review", tags=["HITL Review"])
api_v1_router.include_router(applications.router, prefix="/applications", tags=["Applications"])
api_v1_router.include_router(providers.router, prefix="/providers", tags=["LLM Providers"])
