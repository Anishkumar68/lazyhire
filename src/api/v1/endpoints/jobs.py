from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.schemas.common import ResponseModel
from src.schemas.job import (
    JobPostingCreate,
    JobPostingUpdate,
    JobPostingResponse,
    JobSearchQuery,
    JobScrapeRequest,
    JobIngestRequest,
    JobFitScoreResponse,
)
from src.schemas.profile import JobSearchConfig
from src.services.application_service import ApplicationService
from src.services.job_service import JobService
from src.services.matching_service import MatchingService

router = APIRouter()

DB = Depends(get_db)


@router.get("/", response_model=ResponseModel[List[JobPostingResponse]])
async def list_jobs(
    platform: Optional[str] = None,
    is_easy_apply_only: bool = False,
    match_status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = DB,
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
async def create_job(payload: JobPostingCreate, db: AsyncSession = DB):
    service = JobService(db)
    saved_jobs = await service.bulk_upsert_jobs([payload.model_dump()])
    if not saved_jobs:
        raise HTTPException(status_code=400, detail="Failed to save job posting")
    return ResponseModel(message="Job posting created", data=saved_jobs[0])


@router.get("/{job_id}", response_model=ResponseModel[JobPostingResponse])
async def get_job(job_id: int, db: AsyncSession = DB):
    service = JobService(db)
    job = await service.get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")
    return ResponseModel(data=job)


@router.put("/{job_id}")
async def update_job(job_id: int, payload: JobPostingUpdate, db: AsyncSession = DB):
    """Update job posting details, match status, or fit score."""
    pass


@router.delete("/{job_id}")
async def delete_job(job_id: int, db: AsyncSession = DB):
    """Delete or archive a job posting."""
    pass


@router.post("/scrape")
async def scrape_jobs(payload: JobScrapeRequest):
    """Trigger background scraper across LinkedIn or supported ATS platforms."""
    pass


@router.post("/ingest")
async def ingest_job_url(payload: JobIngestRequest, db: AsyncSession = DB):
    """Direct intake and normalization of an external job description URL."""
    pass


@router.get("/{job_id}/fit-score")
async def get_job_fit_score(job_id: int, candidate_id: Optional[int] = None, db: AsyncSession = DB):
    """Compute and retrieve explainable fit score breakdown (pgvector cosine + heuristic rules)."""
    pass


@router.post("/batch-score")
async def batch_score_jobs(candidate_id: Optional[int] = None, db: AsyncSession = DB):
    """Score all pending unscored jobs against the candidate profile."""
    pass


@router.post("/discover", response_model=ResponseModel[List[JobPostingResponse]])
async def discover_jobs(
    config: JobSearchConfig,
    max_pages: int = 3,
    db: AsyncSession = DB,
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
    db: AsyncSession = DB,
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
