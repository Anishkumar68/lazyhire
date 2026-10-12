from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from src.schemas.job import JobPostingResponse


class ApplicationCreate(BaseModel):
    job_id: int
    resume_id: Optional[int] = None
    cover_letter_id: Optional[int] = None


class ReviewActionRequest(BaseModel):
    action: str  # approve, reject, regenerate
    custom_notes: Optional[str] = None


class BulkReviewActionRequest(BaseModel):
    application_ids: List[int]
    action: str  # approve, reject, regenerate
    custom_notes: Optional[str] = None


class AnswerOverrideRequest(BaseModel):
    answers: Dict[str, Any]


class ApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id: int
    resume_id: Optional[int] = None
    cover_letter_id: Optional[int] = None
    status: str
    applied_at: Optional[datetime] = None
    failure_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ReviewPreviewResponse(BaseModel):
    application_id: int
    job: Optional[JobPostingResponse] = None
    resume_url: Optional[str] = None
    cover_letter_url: Optional[str] = None
    fit_score: Optional[float] = None
    match_reasons: Optional[Dict[str, Any]] = None
    proposed_answers: Optional[Dict[str, Any]] = None
    dry_run_screenshot_url: Optional[str] = None


class ApplicationDetailResponse(ApplicationResponse):
    job: Optional[JobPostingResponse] = None
    form_answers: Optional[Dict[str, Any]] = None
    logs: Optional[List[str]] = None
