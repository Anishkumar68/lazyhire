from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr


class CandidateProfileBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    website_url: Optional[str] = None
    summary: Optional[str] = None
    skills: Optional[List[str]] = None
    work_experience: Optional[List[Dict[str, Any]]] = None
    education: Optional[List[Dict[str, Any]]] = None
    work_authorization: Optional[str] = "Yes"
    requires_sponsorship: Optional[str] = "No"
    desired_salary: Optional[str] = None
    notice_period: Optional[str] = None


class CandidateProfileCreate(CandidateProfileBase):
    pass


class CandidateProfileResponse(CandidateProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class QABankEntryBase(BaseModel):
    question_key: str
    question_text: str
    answer_text: str
    category: str = "general"


class QABankEntryCreate(QABankEntryBase):
    pass


class QABankEntryResponse(QABankEntryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
