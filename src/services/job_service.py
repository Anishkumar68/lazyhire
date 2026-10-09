"""Job Service module.

Manages job intake from scrapers, normalization, database persistence (upsert),
and retrieval of JobPosting records.
"""

from __future__ import annotations

import logging
from typing import Any, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.execution.linkedin_scraper import LinkedInScraper
from src.models.job import JobPosting
from src.schemas.profile import JobSearchConfig

logger = logging.getLogger("lazyhire.services.job")


class JobService:
    """Service layer for job discovery, persistence, and queries."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def run_discovery_and_store(
        self,
        config: JobSearchConfig,
        max_pages: int = 3,
        headless: bool = False,
    ) -> list[JobPosting]:
        """Run LinkedInScraper discovery with config, normalize, deduplicate, and persist to DB."""
        logger.info(
            "Starting job discovery: keywords=%s, location=%s, pages=%d",
            config.keywords,
            config.location,
            max_pages,
        )

        scraper = LinkedInScraper(headless=headless)
        raw_jobs = await scraper.search_jobs(config, max_pages=max_pages)

        logger.info("Scraper returned %d raw jobs. Upserting into DB...", len(raw_jobs))
        saved_jobs = await self.bulk_upsert_jobs(raw_jobs)
        logger.info("Successfully persisted %d jobs to database.", len(saved_jobs))
        return saved_jobs

    async def bulk_upsert_jobs(self, raw_jobs: list[dict[str, Any]]) -> list[JobPosting]:
        """Normalize and upsert raw scraped job dictionaries into the database."""
        saved_jobs: list[JobPosting] = []

        for raw in raw_jobs:
            try:
                external_id = str(raw.get("external_id") or raw.get("link") or raw.get("url") or "").strip()
                if not external_id:
                    continue

                url = str(raw.get("url") or raw.get("link") or "").strip()
                title = str(raw.get("title") or "").strip()
                if not title or not url:
                    continue

                company = str(raw.get("company") or "Unknown").strip()
                location = raw.get("location")
                if location is not None:
                    location = str(location).strip()

                is_easy_apply = bool(raw.get("is_easy_apply", False))
                description = str(raw.get("description") or "").strip()
                platform = str(raw.get("platform") or "linkedin").strip()
                raw_data = raw.get("raw_data") if isinstance(raw.get("raw_data"), dict) else raw

                # Check if job already exists in DB
                result = await self.db.execute(
                    select(JobPosting).where(JobPosting.external_id == external_id)
                )
                existing_job = result.scalar_one_or_none()

                if existing_job:
                    # Update existing record fields
                    existing_job.title = title
                    existing_job.company = company
                    if location:
                        existing_job.location = location
                    existing_job.url = url
                    if description:
                        existing_job.description = description
                    existing_job.is_easy_apply = is_easy_apply
                    existing_job.raw_data = raw_data
                    saved_jobs.append(existing_job)
                else:
                    # Create new JobPosting record
                    new_job = JobPosting(
                        external_id=external_id,
                        platform=platform,
                        title=title,
                        company=company,
                        location=location,
                        url=url,
                        description=description,
                        is_easy_apply=is_easy_apply,
                        match_status="pending",
                        raw_data=raw_data,
                    )
                    self.db.add(new_job)
                    saved_jobs.append(new_job)
            except Exception as exc:
                logger.error("Error processing job %s: %s", raw.get("external_id"), exc)

        await self.db.commit()

        # Refresh all saved objects
        for job in saved_jobs:
            try:
                await self.db.refresh(job)
            except Exception:
                pass

        return saved_jobs

    async def get_job_by_id(self, job_id: int) -> JobPosting | None:
        """Fetch JobPosting by internal primary key."""
        result = await self.db.execute(select(JobPosting).where(JobPosting.id == job_id))
        return result.scalar_one_or_none()

    async def get_job_by_external_id(self, external_id: str) -> JobPosting | None:
        """Fetch JobPosting by unique external_id."""
        result = await self.db.execute(select(JobPosting).where(JobPosting.external_id == external_id))
        return result.scalar_one_or_none()

    async def list_jobs(
        self,
        platform: str | None = None,
        is_easy_apply_only: bool = False,
        match_status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Sequence[JobPosting]:
        """List stored JobPosting records with filters."""
        stmt = select(JobPosting).order_by(JobPosting.id.desc())

        if platform:
            stmt = stmt.where(JobPosting.platform == platform)
        if is_easy_apply_only:
            stmt = stmt.where(JobPosting.is_easy_apply == True)
        if match_status:
            stmt = stmt.where(JobPosting.match_status == match_status)

        stmt = stmt.offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()
