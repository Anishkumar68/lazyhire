"""Profile Service module with Redis caching for high-speed reuse across workers."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.redis import RedisCache
from src.models.profile import CandidateProfile, QABankEntry

logger = logging.getLogger("lazyhire.services.profile")

CACHE_TTL_SECONDS = 3600  # 1 hour cache TTL
PROFILE_CACHE_KEY_PREFIX = "lazyhire:profile:"
ACTIVE_PROFILE_CACHE_KEY = "lazyhire:profile:active"
QA_BANK_CACHE_KEY = "lazyhire:qabank:all"


class ProfileService:
    """Service layer for Candidate Profiles and QA Bank with Redis Caching."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_profile(self, candidate_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve candidate profile by ID. Checks Redis cache first before DB."""
        cache_key = f"{PROFILE_CACHE_KEY_PREFIX}{candidate_id}"

        # 1. Try loading from Redis cache
        cached_profile = await RedisCache.get_json(cache_key)
        if cached_profile:
            logger.debug("Redis cache HIT for profile ID %d", candidate_id)
            return cached_profile

        # 2. DB fallback query
        logger.debug("Redis cache MISS for profile ID %d. Querying DB...", candidate_id)
        result = await self.db.execute(
            select(CandidateProfile).where(CandidateProfile.id == candidate_id)
        )
        profile_model = result.scalar_one_or_none()

        if not profile_model:
            return None

        # Serialize & store into Redis cache for reuse
        profile_dict = self._profile_to_dict(profile_model)
        await RedisCache.set_json(cache_key, profile_dict, ttl_seconds=CACHE_TTL_SECONDS)
        return profile_dict

    async def get_active_profile(self) -> Optional[Dict[str, Any]]:
        """Retrieve the primary/active candidate profile for automation runs."""
        # 1. Check active profile key in Redis
        cached_active = await RedisCache.get_json(ACTIVE_PROFILE_CACHE_KEY)
        if cached_active:
            logger.debug("Redis cache HIT for active candidate profile")
            return cached_active

        # 2. Query DB for most recent candidate profile
        result = await self.db.execute(
            select(CandidateProfile).order_by(CandidateProfile.id.desc()).limit(1)
        )
        profile_model = result.scalar_one_or_none()

        if not profile_model:
            return None

        profile_dict = self._profile_to_dict(profile_model)
        # Store in Redis as active profile and by candidate ID
        await RedisCache.set_json(ACTIVE_PROFILE_CACHE_KEY, profile_dict, ttl_seconds=CACHE_TTL_SECONDS)
        await RedisCache.set_json(f"{PROFILE_CACHE_KEY_PREFIX}{profile_model.id}", profile_dict, ttl_seconds=CACHE_TTL_SECONDS)
        return profile_dict

    async def create_profile(self, profile_data: Dict[str, Any]) -> CandidateProfile:
        """Create new candidate profile in DB and cache it in Redis."""
        # Filter valid model attributes
        valid_data = {k: v for k, v in profile_data.items() if hasattr(CandidateProfile, k)}
        profile = CandidateProfile(**valid_data)
        self.db.add(profile)
        await self.db.commit()
        await self.db.refresh(profile)

        profile_dict = self._profile_to_dict(profile)
        # Cache profile in Redis for immediate reuse
        cache_key = f"{PROFILE_CACHE_KEY_PREFIX}{profile.id}"
        await RedisCache.set_json(cache_key, profile_dict, ttl_seconds=CACHE_TTL_SECONDS)
        await RedisCache.set_json(ACTIVE_PROFILE_CACHE_KEY, profile_dict, ttl_seconds=CACHE_TTL_SECONDS)

        logger.info("Created candidate profile ID %d and loaded into Redis cache", profile.id)
        return profile

    async def update_profile(self, candidate_id: int, update_data: Dict[str, Any]) -> Optional[CandidateProfile]:
        """Update existing candidate profile and refresh Redis cache."""
        result = await self.db.execute(
            select(CandidateProfile).where(CandidateProfile.id == candidate_id)
        )
        profile = result.scalar_one_or_none()
        if not profile:
            return None

        for field, value in update_data.items():
            if value is not None and hasattr(profile, field):
                setattr(profile, field, value)

        await self.db.commit()
        await self.db.refresh(profile)

        # Invalidate & refresh Redis cache
        profile_dict = self._profile_to_dict(profile)
        cache_key = f"{PROFILE_CACHE_KEY_PREFIX}{candidate_id}"
        await RedisCache.set_json(cache_key, profile_dict, ttl_seconds=CACHE_TTL_SECONDS)
        await RedisCache.set_json(ACTIVE_PROFILE_CACHE_KEY, profile_dict, ttl_seconds=CACHE_TTL_SECONDS)

        logger.info("Updated candidate profile ID %d and refreshed Redis cache", candidate_id)
        return profile

    async def get_qa_bank_entries(self) -> List[Dict[str, Any]]:
        """Retrieve QA Bank entries. Checks Redis cache first."""
        cached_qa = await RedisCache.get_json(QA_BANK_CACHE_KEY)
        if cached_qa:
            return cached_qa

        result = await self.db.execute(select(QABankEntry))
        entries = result.scalars().all()
        qa_list = [
            {
                "id": e.id,
                "question_key": e.question_key,
                "question_text": e.question_text,
                "answer_text": e.answer_text,
                "category": e.category,
            }
            for e in entries
        ]
        await RedisCache.set_json(QA_BANK_CACHE_KEY, qa_list, ttl_seconds=CACHE_TTL_SECONDS)
        return qa_list

    async def add_qa_entry(self, qa_data: Dict[str, Any]) -> QABankEntry:
        """Add new QA entry and invalidate QA bank Redis cache."""
        valid_data = {k: v for k, v in qa_data.items() if hasattr(QABankEntry, k)}
        entry = QABankEntry(**valid_data)
        self.db.add(entry)
        await self.db.commit()
        await self.db.refresh(entry)

        # Invalidate QA bank cache so next lookup re-fetches updated list
        await RedisCache.delete(QA_BANK_CACHE_KEY)
        return entry

    def _profile_to_dict(self, p: CandidateProfile) -> Dict[str, Any]:
        return {
            "id": p.id,
            "first_name": p.first_name,
            "last_name": p.last_name,
            "email": p.email,
            "phone": p.phone,
            "location": p.location,
            "linkedin_url": p.linkedin_url,
            "github_url": p.github_url,
            "website_url": p.website_url,
            "summary": p.summary,
            "skills": p.skills or [],
            "total_work_experience": p.total_work_experience,
            "education": p.education or [],
            "keywords": p.keywords or [],
            "work_authorization": p.work_authorization,
            "requires_sponsorship": p.requires_sponsorship,
            "expected_ctc": p.expected_ctc,
            "current_ctc": p.current_ctc,
            "notice_period": p.notice_period,
        }
