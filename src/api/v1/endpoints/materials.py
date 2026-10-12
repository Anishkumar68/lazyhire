from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.core.database import get_db
from src.models.material import TailoredDocument
from src.schemas.common import ResponseModel
from src.schemas.material import (
    MaterialGenerateRequest,
    ResumeTailorRequest,
    CoverLetterTailorRequest,
    DocumentCompileRequest,
    TailoredDocumentUpdate,
    TailoredDocumentResponse,
)

router = APIRouter()

DB = Depends(get_db)


@router.post("/generate", response_model=ResponseModel[dict])
async def generate_material(payload: MaterialGenerateRequest, db: AsyncSession = DB):
    """Trigger generic material generation background task."""
    return ResponseModel(
        message="Material generation task enqueued",
        data={
            "task_id": "task_mat_gen_456",
            "job_id": payload.job_id,
            "doc_type": payload.doc_type,
            "status": "queued",
        },
    )


@router.get("/job/{job_id}", response_model=ResponseModel[List[TailoredDocumentResponse]])
async def get_materials_for_job(job_id: int, db: AsyncSession = DB):
    """Retrieve all tailored documents generated for a specific job."""
    result = await db.execute(select(TailoredDocument).where(TailoredDocument.job_id == job_id))
    docs = result.scalars().all()
    return ResponseModel(data=list(docs))


@router.post("/tailor/resume")
async def tailor_resume(payload: ResumeTailorRequest, db: AsyncSession = DB):
    """Generate job-grounded resume intermediate representation (IR) and compile to target format."""
    pass


@router.post("/tailor/cover-letter")
async def tailor_cover_letter(payload: CoverLetterTailorRequest, db: AsyncSession = DB):
    """Generate grounded cover letter tailored to the job description."""
    pass


@router.get("/{document_id}")
async def get_material(document_id: int, db: AsyncSession = DB):
    """Get tailored document details, IR content, and compile state."""
    pass


@router.put("/{document_id}")
async def update_material(document_id: int, payload: TailoredDocumentUpdate, db: AsyncSession = DB):
    """Manual override/edit of tailored document content or LaTeX template."""
    pass


@router.post("/{document_id}/compile")
async def compile_material(document_id: int, payload: DocumentCompileRequest, db: AsyncSession = DB):
    """Compile tailored document to PDF, DOCX, Markdown, or HTML via tectonic/pandoc."""
    pass


@router.get("/{document_id}/download")
async def download_material(document_id: int, db: AsyncSession = DB):
    """Download compiled binary file (PDF/DOCX) of the tailored document."""
    pass


@router.post("/{document_id}/validate-grounding")
async def validate_document_grounding(document_id: int, db: AsyncSession = DB):
    """Run fact-drift and hallucination guardrail verification against candidate profile facts."""
    pass


@router.delete("/{document_id}")
async def delete_material(document_id: int, db: AsyncSession = DB):
    """Delete or archive tailored document artifact."""
    pass
