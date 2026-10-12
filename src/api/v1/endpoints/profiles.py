from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.schemas.common import ResponseModel
from src.schemas.profile import (
    CandidateProfileCreate,
    CandidateProfileUpdate,
    CandidateProfileResponse,
    QABankEntryCreate,
    QABankEntryUpdate,
    QABankEntryResponse,
    StoryEntryCreate,
    StoryEntryUpdate,
    StoryEntryResponse,
)
from src.services.profile_service import ProfileService

router = APIRouter()

DB = Depends(get_db)


@router.get("/active", response_model=ResponseModel[Optional[Dict[str, Any]]])
async def get_active_profile(db: AsyncSession = DB):
    """Retrieve the primary active candidate profile from Redis cache (with DB fallback)."""
    service = ProfileService(db)
    profile = await service.get_active_profile()
    if not profile:
        return ResponseModel(message="No active candidate profile found", data=None)
    return ResponseModel(message="Active profile loaded from Redis cache", data=profile)


@router.get("/{candidate_id}", response_model=ResponseModel[Dict[str, Any]])
async def get_profile_by_id(candidate_id: int, db: AsyncSession = DB):
    """Retrieve candidate profile by ID using Redis cache first."""
    service = ProfileService(db)
    profile = await service.get_profile(candidate_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Candidate profile not found")
    return ResponseModel(message="Profile retrieved", data=profile)


@router.post("/", response_model=ResponseModel[CandidateProfileResponse], status_code=status.HTTP_201_CREATED)
async def create_profile(payload: CandidateProfileCreate, db: AsyncSession = DB):
    """Create a new candidate profile in DB and load it into Redis cache for reuse."""
    service = ProfileService(db)
    profile = await service.create_profile(payload.model_dump())
    return ResponseModel(message="Profile created and cached in Redis successfully", data=profile)


@router.put("/{candidate_id}", response_model=ResponseModel[CandidateProfileResponse])
async def update_profile(
    candidate_id: int,
    payload: CandidateProfileUpdate,
    db: AsyncSession = DB
):
    """Update candidate profile in DB and refresh Redis cache."""
    service = ProfileService(db)
    updated_profile = await service.update_profile(candidate_id, payload.model_dump(exclude_unset=True))
    if not updated_profile:
        raise HTTPException(status_code=404, detail="Candidate profile not found")
    return ResponseModel(message="Profile updated and Redis cache refreshed", data=updated_profile)


@router.post("/{candidate_id}/upload-resume")
async def upload_resume(candidate_id: int, file: UploadFile = File(...), db: AsyncSession = DB):
    """Upload and parse an existing PDF resume into structured applicant memory bank facts."""
    pass


# --- Applicant Memory Bank: Story Bank Endpoints ---

@router.get("/{candidate_id}/stories")
async def list_stories(candidate_id: int, db: AsyncSession = DB):
    """List applicant story bank entries and bullet point pool."""
    pass


@router.post("/{candidate_id}/stories")
async def create_story(candidate_id: int, payload: StoryEntryCreate, db: AsyncSession = DB):
    """Add a new story / accomplishment bullet point to the candidate's memory bank."""
    pass


@router.put("/{candidate_id}/stories/{story_id}")
async def update_story(candidate_id: int, story_id: int, payload: StoryEntryUpdate, db: AsyncSession = DB):
    """Update an existing story / accomplishment bullet point."""
    pass


@router.delete("/{candidate_id}/stories/{story_id}")
async def delete_story(candidate_id: int, story_id: int, db: AsyncSession = DB):
    """Delete a story from the memory bank."""
    pass


# --- Dynamic QA Bank Endpoints ---

@router.get("/qa-bank/list", response_model=ResponseModel[List[Dict[str, Any]]])
async def get_qa_entries(db: AsyncSession = DB):
    """Get all QA Bank entries cached in Redis."""
    service = ProfileService(db)
    entries = await service.get_qa_bank_entries()
    return ResponseModel(message="QA entries loaded from cache", data=entries)


@router.post("/qa-bank", response_model=ResponseModel[QABankEntryResponse], status_code=status.HTTP_201_CREATED)
async def add_qa_entry(payload: QABankEntryCreate, db: AsyncSession = DB):
    """Add a new QA Bank entry and invalidate QA Redis cache."""
    service = ProfileService(db)
    entry = await service.add_qa_entry(payload.model_dump())
    return ResponseModel(message="QA entry added and cache updated", data=entry)


@router.put("/qa-bank/{entry_id}")
async def update_qa_entry(entry_id: int, payload: QABankEntryUpdate, db: AsyncSession = DB):
    """Update a QA Bank entry."""
    pass


@router.delete("/qa-bank/{entry_id}")
async def delete_qa_entry(entry_id: int, db: AsyncSession = DB):
    """Delete a QA Bank entry."""
    pass
