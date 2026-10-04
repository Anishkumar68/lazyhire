from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.core.database import get_db
from src.models.job import JobPosting
from src.schemas.common import ResponseModel
from src.schemas.job import JobPostingCreate, JobPostingResponse, JobSearchQuery

router = APIRouter()


@router.get("/", response_model=ResponseModel[List[JobPostingResponse]])
async def list_jobs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(JobPosting).order_by(JobPosting.id.desc()))
    jobs = result.scalars().all()
    return ResponseModel(data=list(jobs))


@router.post("/", response_model=ResponseModel[JobPostingResponse], status_code=status.HTTP_201_CREATED)
async def create_job(payload: JobPostingCreate, db: AsyncSession = Depends(get_db)):
    job = JobPosting(**payload.model_dump())
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return ResponseModel(message="Job posting created", data=job)


@router.get("/{job_id}", response_model=ResponseModel[JobPostingResponse])
async def get_job(job_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(JobPosting).where(JobPosting.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")
    return ResponseModel(data=job)


@router.post("/search", response_model=ResponseModel[dict])
async def search_jobs(query: JobSearchQuery):
    # Search dispatch trigger endpoint (will interface with search worker/intake service)
    return ResponseModel(
        message="Search task initiated",
        data={
            "query": query.model_dump(),
            "status": "queued",
            "task_id": "stub_search_task_123"
        }
    )
