from typing import Optional
from sqlalchemy import Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base
from src.models.base import TimestampMixin


class CandidateProfile(Base, TimestampMixin):
    __tablename__ = "candidate_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    github_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    website_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Structured resume data & skills
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    skills: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # ["Python", "FastAPI", "PostgreSQL"]
    total_work_experience: Mapped[Optional[int]] = mapped_column(Integer, nullable=True) #3,4,5
    education: Mapped[Optional[list[dict]]] = mapped_column(JSON, nullable=True)
    keywords: Mapped[list[str]] = mapped_column(JSON, default=list)
    
    # Equal opportunity & legal authorization default answers
    work_authorization: Mapped[Optional[str]] = mapped_column(String(50), default="Yes")
    requires_sponsorship: Mapped[Optional[str]] = mapped_column(String(50), default="No")
    expected_ctc: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    current_ctc:Mapped[Optional[int]]= mapped_column(Integer,nullable=True)
    notice_period: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)


class QABankEntry(Base, TimestampMixin):
    __tablename__ = "qa_bank_entries"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    question_key: Mapped[str] = mapped_column(String(255), index=True) # e.g. "years_of_experience_python"
    question_text: Mapped[str] = mapped_column(Text)
    answer_text: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(50), default="general", index=True)
