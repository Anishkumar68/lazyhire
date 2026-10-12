from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.core.database import get_db
from src.models.application import JobApplication
from src.schemas.common import ResponseModel
from src.schemas.application import (
    ApplicationResponse,
    ReviewActionRequest,
    BulkReviewActionRequest,
    AnswerOverrideRequest,
)

router = APIRouter()

DB = Depends(get_db)


@router.get("/queue", response_model=ResponseModel[List[ApplicationResponse]])
async def get_review_queue(db: AsyncSession = DB):
    """List all job applications pending human operator review."""
    result = await db.execute(
        select(JobApplication)
        .where(JobApplication.status == "pending_review")
        .order_by(JobApplication.id.asc())
    )
    apps = result.scalars().all()
    return ResponseModel(data=list(apps))


@router.get("/{application_id}/preview")
async def get_review_preview(application_id: int, db: AsyncSession = DB):
    """Retrieve full pre-submission review package including job match breakdown, tailored materials, dry run screenshot, and form answers."""
    pass


@router.post("/{application_id}/action", response_model=ResponseModel[ApplicationResponse])
async def process_review_action(
    application_id: int,
    payload: ReviewActionRequest,
    db: AsyncSession = DB
):
    """Process review decision (approve, reject, regenerate) on a single application."""
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


@router.post("/bulk-action")
async def bulk_review_action(payload: BulkReviewActionRequest, db: AsyncSession = DB):
    """Apply bulk approval or rejection across multiple applications."""
    pass


@router.put("/{application_id}/answers")
async def update_application_answers(application_id: int, payload: AnswerOverrideRequest, db: AsyncSession = DB):
    """Operator override of dynamic form question answers prior to bot submission."""
    pass
