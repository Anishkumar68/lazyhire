from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.schemas.common import ResponseModel
from src.schemas.profile import (
    CandidateProfileCreate,
    CandidateProfileUpdate,
    CandidateProfileResponse,
    QABankEntryCreate,
    QABankEntryResponse,
)
from src.services.profile_service import ProfileService

router = APIRouter()


@router.get("/active", response_model=ResponseModel[Optional[Dict[str, Any]]])
async def get_active_profile(db: AsyncSession = Depends(get_db)):
    """Retrieve the primary active candidate profile from Redis cache (with DB fallback)."""
    service = ProfileService(db)
    profile = await service.get_active_profile()
    if not profile:
        return ResponseModel(message="No active candidate profile found", data=None)
    return ResponseModel(message="Active profile loaded from Redis cache", data=profile)


@router.get("/{candidate_id}", response_model=ResponseModel[Dict[str, Any]])
async def get_profile_by_id(candidate_id: int, db: AsyncSession = Depends(get_db)):
    """Retrieve candidate profile by ID using Redis cache first."""
    service = ProfileService(db)
    profile = await service.get_profile(candidate_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Candidate profile not found")
    return ResponseModel(message="Profile retrieved", data=profile)


@router.post("/", response_model=ResponseModel[CandidateProfileResponse], status_code=status.HTTP_201_CREATED)
async def create_profile(payload: CandidateProfileCreate, db: AsyncSession = Depends(get_db)):
    """Create a new candidate profile in DB and load it into Redis cache for reuse."""
    service = ProfileService(db)
    profile = await service.create_profile(payload.model_dump())
    return ResponseModel(message="Profile created and cached in Redis successfully", data=profile)


@router.put("/{candidate_id}", response_model=ResponseModel[CandidateProfileResponse])
async def update_profile(
    candidate_id: int,
    payload: CandidateProfileUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update candidate profile in DB and refresh Redis cache."""
    service = ProfileService(db)
    updated_profile = await service.update_profile(candidate_id, payload.model_dump(exclude_unset=True))
    if not updated_profile:
        raise HTTPException(status_code=404, detail="Candidate profile not found")
    return ResponseModel(message="Profile updated and Redis cache refreshed", data=updated_profile)


@router.get("/qa-bank/list", response_model=ResponseModel[List[Dict[str, Any]]])
async def get_qa_entries(db: AsyncSession = Depends(get_db)):
    """Get all QA Bank entries cached in Redis."""
    service = ProfileService(db)
    entries = await service.get_qa_bank_entries()
    return ResponseModel(message="QA entries loaded from cache", data=entries)


@router.post("/qa-bank", response_model=ResponseModel[QABankEntryResponse], status_code=status.HTTP_201_CREATED)
async def add_qa_entry(payload: QABankEntryCreate, db: AsyncSession = Depends(get_db)):
    """Add a new QA Bank entry and invalidate QA Redis cache."""
    service = ProfileService(db)
    entry = await service.add_qa_entry(payload.model_dump())
    return ResponseModel(message="QA entry added and cache updated", data=entry)
