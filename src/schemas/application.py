from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ApplicationCreate(BaseModel):
    job_id: int
    resume_id: Optional[int] = None
    cover_letter_id: Optional[int] = None


class ReviewActionRequest(BaseModel):
    action: str  # approve, reject, regenerate
    custom_notes: Optional[str] = None


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
