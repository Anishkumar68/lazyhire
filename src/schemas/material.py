from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class MaterialGenerateRequest(BaseModel):
    job_id: int
    doc_type: str = "resume"  # resume, cover_letter
    format: str = "pdf"       # pdf, docx, txt, md, html
    custom_instructions: Optional[str] = None


class ResumeTailorRequest(BaseModel):
    job_id: int
    candidate_id: Optional[int] = None
    format: str = "pdf"  # pdf, latex, docx, markdown
    custom_instructions: Optional[str] = None
    enable_drift_check: bool = True


class CoverLetterTailorRequest(BaseModel):
    job_id: int
    candidate_id: Optional[int] = None
    format: str = "pdf"
    tone: str = "professional"  # professional, confident, enthusiastic
    custom_instructions: Optional[str] = None


class DocumentCompileRequest(BaseModel):
    format: str = "pdf"  # pdf, docx, markdown, html, latex


class TailoredDocumentUpdate(BaseModel):
    content_text: Optional[str] = None
    file_path: Optional[str] = None
    format: Optional[str] = None


class GroundingValidationResponse(BaseModel):
    document_id: int
    is_valid: bool = True
    hallucination_detected: bool = False
    drift_score: float = 0.0
    flagged_claims: List[str] = Field(default_factory=list)
    grounded_facts_count: int = 0


class TailoredDocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id: int
    doc_type: str
    file_path: Optional[str] = None
    format: str
    content_text: Optional[str] = None
    created_at: datetime
    updated_at: datetime
