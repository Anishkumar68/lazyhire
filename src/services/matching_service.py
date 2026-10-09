"""Best-fit Ranking and Filtering Service.

Ranks pending JobPosting records against candidate profiles and updates match_status & fit_score.
"""

from __future__ import annotations

import logging
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.job import JobPosting
from src.models.profile import CandidateProfile
from src.services.fit_scorer import FitScorer

logger = logging.getLogger("lazyhire.services.matching")


class MatchingService:
    """Service for scoring, filtering, and ranking job postings."""

    def __init__(self, db: AsyncSession, scorer: FitScorer | None = None):
        self.db = db
        self.scorer = scorer or FitScorer()

    async def score_and_rank_pending_jobs(
        self,
        candidate_id: int | None = None,
        min_threshold: float = 0.5,
    ) -> Sequence[JobPosting]:
        """Score all pending job postings against a CandidateProfile and update database records."""
        # Retrieve CandidateProfile
        stmt = select(CandidateProfile)
        if candidate_id:
            stmt = stmt.where(CandidateProfile.id == candidate_id)
        result = await self.db.execute(stmt)
        profile = result.scalars().first()

        if not profile:
            logger.warning("No candidate profile found for matching.")
            return []

        # Query pending job postings
        jobs_result = await self.db.execute(
            select(JobPosting).where(JobPosting.match_status == "pending")
        )
        pending_jobs = jobs_result.scalars().all()

        logger.info("Found %d pending jobs to evaluate against profile %s", len(pending_jobs), profile.email)

        matched_jobs: list[JobPosting] = []

        for job in pending_jobs:
            fit_score, passes_filter, match_reasons = self.scorer.evaluate_fit(profile, job)
            job.fit_score = fit_score
            job.match_reasons = match_reasons

            if passes_filter and fit_score >= min_threshold:
                job.match_status = "matched"
                matched_jobs.append(job)
            else:
                job.match_status = "rejected"

        await self.db.commit()

        # Sort matched jobs descending by fit_score
        matched_jobs.sort(key=lambda j: j.fit_score or 0.0, reverse=True)
        return matched_jobs

    async def get_ranked_matched_jobs(self, limit: int = 50) -> Sequence[JobPosting]:
        """Fetch all matched jobs ranked descending by fit_score."""
        stmt = (
            select(JobPosting)
            .where(JobPosting.match_status == "matched")
            .order_by(JobPosting.fit_score.desc().nullslast(), JobPosting.id.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()
