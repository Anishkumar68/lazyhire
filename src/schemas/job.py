from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class JobPostingBase(BaseModel):
    external_id: str
    platform: str
    title: str
    company: str
    location: Optional[str] = None
    url: str
    description: str
    is_easy_apply: bool = False


class JobPostingCreate(JobPostingBase):
    raw_data: Optional[Dict[str, Any]] = None


class JobPostingResponse(JobPostingBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    fit_score: Optional[float] = None
    match_status: str = "pending"
    match_reasons: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class JobSearchQuery(BaseModel):
    keywords: str
    location: Optional[str] = None
    platform: str = "linkedin"
    is_easy_apply_only: bool = True
    limit: int = 50
