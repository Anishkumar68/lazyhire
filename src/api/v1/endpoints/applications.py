from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.core.database import get_db
from src.models.application import JobApplication
from src.schemas.common import ResponseModel
from src.schemas.application import ApplicationCreate, ApplicationResponse

router = APIRouter()


@router.get("/", response_model=ResponseModel[List[ApplicationResponse]])
async def list_applications(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(JobApplication).order_by(JobApplication.id.desc()))
    apps = result.scalars().all()
    return ResponseModel(data=list(apps))


@router.post("/", response_model=ResponseModel[ApplicationResponse], status_code=status.HTTP_201_CREATED)
async def create_application(payload: ApplicationCreate, db: AsyncSession = Depends(get_db)):
    app = JobApplication(**payload.model_dump())
    db.add(app)
    await db.commit()
    await db.refresh(app)
    return ResponseModel(message="Application queued", data=app)


@router.post("/{application_id}/submit", response_model=ResponseModel[dict])
async def trigger_submission(application_id: int, db: AsyncSession = Depends(get_db)):
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
