from fastapi import APIRouter
from src.api.v1.endpoints import (
    health,
    jobs,
    profiles,
    materials,
    review,
    applications,
    execution,
    providers,
    tasks,
    analytics,
)

api_v1_router = APIRouter()

api_v1_router.include_router(health.router, tags=["Health"])
api_v1_router.include_router(jobs.router, prefix="/jobs", tags=["Jobs & Intake"])
api_v1_router.include_router(profiles.router, prefix="/profiles", tags=["Profiles & Memory Bank"])
api_v1_router.include_router(materials.router, prefix="/materials", tags=["Materials & Resumes"])
api_v1_router.include_router(review.router, prefix="/review", tags=["HITL Review Queue"])
api_v1_router.include_router(applications.router, prefix="/applications", tags=["Applications Lifecycle"])
api_v1_router.include_router(execution.router, prefix="/execution", tags=["Live Execution & Stealth Bot"])
api_v1_router.include_router(providers.router, prefix="/providers", tags=["LLM Providers"])
api_v1_router.include_router(tasks.router, prefix="/tasks", tags=["Task Queues & DLQ"])
api_v1_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics & Exports"])
