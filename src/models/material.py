from typing import Optional
from sqlalchemy import String, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base
from src.models.base import TimestampMixin


class TailoredDocument(Base, TimestampMixin):
    __tablename__ = "tailored_documents"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("job_postings.id", ondelete="CASCADE"), index=True)
    doc_type: Mapped[str] = mapped_column(String(50), index=True)  # resume, cover_letter
    file_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    format: Mapped[str] = mapped_column(String(20), default="pdf")  # pdf, docx, txt, md, html
    content_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ir_payload: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Intermediate Representation JSON
