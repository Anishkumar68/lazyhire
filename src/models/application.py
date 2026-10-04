from typing import Optional
from datetime import datetime
from sqlalchemy import String, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base
from src.models.base import TimestampMixin


class JobApplication(Base, TimestampMixin):
    __tablename__ = "job_applications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("job_postings.id", ondelete="CASCADE"), unique=True, index=True)
    resume_id: Mapped[Optional[int]] = mapped_column(ForeignKey("tailored_documents.id"), nullable=True)
    cover_letter_id: Mapped[Optional[int]] = mapped_column(ForeignKey("tailored_documents.id"), nullable=True)
    
    # State machine: draft, pending_review, approved, submitting, submitted, failed, skipped
    status: Mapped[str] = mapped_column(String(50), default="pending_review", index=True)
    applied_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    failure_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    submission_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
