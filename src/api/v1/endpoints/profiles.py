from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.core.database import get_db
from src.models.profile import CandidateProfile, QABankEntry
from src.schemas.common import ResponseModel
from src.schemas.profile import (
    CandidateProfileCreate, CandidateProfileResponse,
    QABankEntryCreate, QABankEntryResponse
)

router = APIRouter()


@router.get("/", response_model=ResponseModel[List[CandidateProfileResponse]])
async def get_profiles(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CandidateProfile))
    profiles = result.scalars().all()
    return ResponseModel(data=list(profiles))


@router.post("/", response_model=ResponseModel[CandidateProfileResponse], status_code=status.HTTP_201_CREATED)
async def create_profile(payload: CandidateProfileCreate, db: AsyncSession = Depends(get_db)):
    profile = CandidateProfile(**payload.model_dump())
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return ResponseModel(message="Profile created successfully", data=profile)


@router.get("/qa-bank", response_model=ResponseModel[List[QABankEntryResponse]])
async def get_qa_entries(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(QABankEntry))
    entries = result.scalars().all()
    return ResponseModel(data=list(entries))


@router.post("/qa-bank", response_model=ResponseModel[QABankEntryResponse], status_code=status.HTTP_201_CREATED)
async def add_qa_entry(payload: QABankEntryCreate, db: AsyncSession = Depends(get_db)):
    entry = QABankEntry(**payload.model_dump())
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return ResponseModel(message="QA entry added", data=entry)
