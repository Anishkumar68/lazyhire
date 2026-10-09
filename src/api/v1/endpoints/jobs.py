from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.schemas.common import ResponseModel
from src.schemas.job import JobPostingCreate, JobPostingResponse, JobSearchQuery
from src.schemas.profile import JobSearchConfig
from src.services.application_service import ApplicationService
from src.services.job_service import JobService
from src.services.matching_service import MatchingService

router = APIRouter()


@router.get("/", response_model=ResponseModel[List[JobPostingResponse]])
async def list_jobs(
    platform: Optional[str] = None,
    is_easy_apply_only: bool = False,
    match_status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    service = JobService(db)
    jobs = await service.list_jobs(
        platform=platform,
        is_easy_apply_only=is_easy_apply_only,
        match_status=match_status,
        limit=limit,
        offset=offset,
    )
    return ResponseModel(data=list(jobs))


@router.post("/", response_model=ResponseModel[JobPostingResponse], status_code=status.HTTP_201_CREATED)
async def create_job(payload: JobPostingCreate, db: AsyncSession = Depends(get_db)):
    service = JobService(db)
    saved_jobs = await service.bulk_upsert_jobs([payload.model_dump()])
    if not saved_jobs:
        raise HTTPException(status_code=400, detail="Failed to save job posting")
    return ResponseModel(message="Job posting created", data=saved_jobs[0])


@router.get("/{job_id}", response_model=ResponseModel[JobPostingResponse])
async def get_job(job_id: int, db: AsyncSession = Depends(get_db)):
    service = JobService(db)
    job = await service.get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")
    return ResponseModel(data=job)


@router.post("/discover", response_model=ResponseModel[List[JobPostingResponse]])
async def discover_jobs(
    config: JobSearchConfig,
    max_pages: int = 3,
    db: AsyncSession = Depends(get_db),
):
    """Trigger scraper discovery, deduplicate, and persist jobs to the DB."""
    service = JobService(db)
    saved_jobs = await service.run_discovery_and_store(config, max_pages=max_pages)
    return ResponseModel(
        message=f"Discovered and stored {len(saved_jobs)} jobs",
        data=list(saved_jobs),
    )


@router.post("/match", response_model=ResponseModel[List[JobPostingResponse]])
async def match_and_rank_jobs(
    candidate_id: Optional[int] = None,
    min_threshold: float = 0.5,
    auto_enqueue: bool = True,
    db: AsyncSession = Depends(get_db),
):
    """Score pending jobs against candidate profile, update match status & fit scores, and enqueue matched jobs."""
    matching_service = MatchingService(db)
    matched_jobs = await matching_service.score_and_rank_pending_jobs(
        candidate_id=candidate_id,
        min_threshold=min_threshold,
    )

    if auto_enqueue:
        app_service = ApplicationService(db)
        await app_service.enqueue_applications_for_matched_jobs()

    return ResponseModel(
        message=f"Matched and ranked {len(matched_jobs)} jobs",
        data=list(matched_jobs),
    )


@router.post("/search", response_model=ResponseModel[dict])
async def search_jobs(query: JobSearchQuery):
    """Trigger search task dispatch."""
    return ResponseModel(
        message="Search task initiated",
        data={
            "query": query.model_dump(),
            "status": "queued",
            "task_id": "search_task_intake",
        },
    )
