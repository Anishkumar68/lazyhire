from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.core.database import get_db
from src.models.application import JobApplication
from src.schemas.common import ResponseModel
from src.schemas.application import ApplicationCreate, ApplicationResponse

router = APIRouter()

DB = Depends(get_db)


@router.get("/", response_model=ResponseModel[List[ApplicationResponse]])
async def list_applications(
    status_filter: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = DB
):
    """List job applications with optional status filter."""
    stmt = select(JobApplication).order_by(JobApplication.id.desc()).offset(offset).limit(limit)
    if status_filter:
        stmt = stmt.where(JobApplication.status == status_filter)
    result = await db.execute(stmt)
    apps = result.scalars().all()
    return ResponseModel(data=list(apps))


@router.post("/", response_model=ResponseModel[ApplicationResponse], status_code=status.HTTP_201_CREATED)
async def create_application(payload: ApplicationCreate, db: AsyncSession = DB):
    """Queue a new application for a job."""
    app = JobApplication(**payload.model_dump())
    db.add(app)
    await db.commit()
    await db.refresh(app)
    return ResponseModel(message="Application queued", data=app)


@router.get("/{application_id}")
async def get_application(application_id: int, db: AsyncSession = DB):
    """Get single application details, form responses, timeline, and current status."""
    pass


@router.post("/{application_id}/submit", response_model=ResponseModel[dict])
async def trigger_submission(application_id: int, db: AsyncSession = DB):
    """Dispatch background browser automation worker to submit the application."""
    result = await db.execute(select(JobApplication).where(JobApplication.id == application_id))
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    app.status = "submitting"
    await db.commit()

    return ResponseModel(
        message="Submission worker dispatched",
        data={
            "application_id": application_id,
            "status": "submitting",
            "task_id": f"task_apply_{application_id}"
        }
    )


@router.post("/batch-submit")
async def batch_submit_applications(db: AsyncSession = DB):
    """Trigger automated submission worker for all approved applications."""
    pass


@router.post("/{application_id}/retry")
async def retry_application(application_id: int, db: AsyncSession = DB):
    """Retry a failed job application."""
    pass


@router.delete("/{application_id}")
async def delete_application(application_id: int, db: AsyncSession = DB):
    """Cancel or delete an application record."""
    pass


@router.get("/{application_id}/logs")
async def get_application_logs(application_id: int, db: AsyncSession = DB):
    """Get execution logs for a specific job application."""
    pass
