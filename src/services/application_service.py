"""Application Queue & Review Gate Service.

Manages enqueuing matched jobs into JobApplication records, review states, and submission tracking.
"""

from __future__ import annotations

import logging
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.application import JobApplication
from src.models.job import JobPosting

logger = logging.getLogger("lazyhire.services.application")


class ApplicationService:
    """Service for managing the job application queue and status transitions."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def enqueue_applications_for_matched_jobs(
        self,
        is_easy_apply_only: bool = True,
    ) -> list[JobApplication]:
        """Enqueue matched jobs into JobApplication table for HITL review / automated submission."""
        stmt = select(JobPosting).where(JobPosting.match_status == "matched")
        if is_easy_apply_only:
            stmt = stmt.where(JobPosting.is_easy_apply == True)

        result = await self.db.execute(stmt)
        matched_jobs = result.scalars().all()

        enqueued_applications: list[JobApplication] = []

        for job in matched_jobs:
            # Check if JobApplication already exists for this job_id
            app_result = await self.db.execute(
                select(JobApplication).where(JobApplication.job_id == job.id)
            )
            existing_app = app_result.scalar_one_or_none()

            if not existing_app:
                new_app = JobApplication(
                    job_id=job.id,
                    status="pending_review",
                    submission_metadata={
                        "platform": job.platform,
                        "url": job.url,
                        "is_easy_apply": job.is_easy_apply,
                    },
                )
                self.db.add(new_app)
                enqueued_applications.append(new_app)
            else:
                enqueued_applications.append(existing_app)

        await self.db.commit()

        for app in enqueued_applications:
            try:
                await self.db.refresh(app)
            except Exception:
                pass

        return enqueued_applications

    async def list_queue(
        self,
        status_filter: str | None = "pending_review",
        limit: int = 50,
        offset: int = 0,
    ) -> Sequence[JobApplication]:
        """Fetch JobApplication records filtered by status."""
        stmt = select(JobApplication).order_by(JobApplication.id.desc())
        if status_filter:
            stmt = stmt.where(JobApplication.status == status_filter)
        stmt = stmt.offset(offset).limit(limit)

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def update_application_status(
        self,
        application_id: int,
        new_status: str,
        failure_reason: str | None = None,
    ) -> JobApplication | None:
        """Transition application state (e.g. pending_review -> approved -> submitting -> submitted/failed)."""
        result = await self.db.execute(
            select(JobApplication).where(JobApplication.id == application_id)
        )
        app = result.scalar_one_or_none()
        if not app:
            return None

        app.status = new_status
        if failure_reason:
            app.failure_reason = failure_reason

        await self.db.commit()
        await self.db.refresh(app)
        return app
