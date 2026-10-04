from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.core.database import get_db
from src.models.application import JobApplication
from src.schemas.common import ResponseModel
from src.schemas.application import ApplicationResponse, ReviewActionRequest

router = APIRouter()


@router.get("/queue", response_model=ResponseModel[List[ApplicationResponse]])
async def get_review_queue(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(JobApplication)
        .where(JobApplication.status == "pending_review")
        .order_by(JobApplication.id.asc())
    )
    apps = result.scalars().all()
    return ResponseModel(data=list(apps))


@router.post("/{application_id}/action", response_model=ResponseModel[ApplicationResponse])
async def process_review_action(
    application_id: int,
    payload: ReviewActionRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(JobApplication).where(JobApplication.id == application_id))
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    if payload.action == "approve":
        app.status = "approved"
    elif payload.action == "reject":
        app.status = "skipped"
    elif payload.action == "regenerate":
        app.status = "draft"
    else:
        raise HTTPException(status_code=400, detail=f"Invalid action: {payload.action}")

    await db.commit()
    await db.refresh(app)
    return ResponseModel(message=f"Application status updated to {app.status}", data=app)
