from typing import Optional
from sqlalchemy import String, Text, Float, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base
from src.models.base import TimestampMixin


class JobPosting(Base, TimestampMixin):
    __tablename__ = "job_postings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    external_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    platform: Mapped[str] = mapped_column(String(50), index=True)  # e.g., linkedin, greenhouse, lever
    title: Mapped[str] = mapped_column(String(255), index=True)
    company: Mapped[str] = mapped_column(String(255), index=True)
    location: Mapped[str] = mapped_column(String(255), nullable=True)
    url: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    is_easy_apply: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    
    # Matching metadata
    fit_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    match_status: Mapped[str] = mapped_column(String(50), default="pending", index=True)  # pending, matched, rejected
    match_reasons: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Original raw data
    raw_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
