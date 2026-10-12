from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


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


class JobPostingUpdate(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None
    is_easy_apply: Optional[bool] = None
    match_status: Optional[str] = None
    fit_score: Optional[float] = None


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


class JobScrapeRequest(BaseModel):
    platform: str = "linkedin"  # linkedin, greenhouse, lever, ashby, workday
    keywords: List[str] = Field(default_factory=list)
    location: Optional[str] = None
    easy_apply_only: bool = True
    remote_only: bool = False
    experience_levels: Optional[List[str]] = None
    max_pages: int = 3


class JobIngestRequest(BaseModel):
    url: str
    platform: Optional[str] = None  # linkedin, greenhouse, lever, ashby, workday
    raw_html_or_text: Optional[str] = None


class JobFitScoreResponse(BaseModel):
    job_id: int
    fit_score: float
    match_status: str
    skills_match: List[str] = Field(default_factory=list)
    missing_keywords: List[str] = Field(default_factory=list)
    seniority_score: float = 1.0
    explanation: Optional[str] = None
