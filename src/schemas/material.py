from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class MaterialGenerateRequest(BaseModel):
    job_id: int
    doc_type: str = "resume"  # resume, cover_letter
    format: str = "pdf"       # pdf, docx, txt, md, html
    custom_instructions: Optional[str] = None


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
