from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.core.database import get_db
from src.models.material import TailoredDocument
from src.schemas.common import ResponseModel
from src.schemas.material import MaterialGenerateRequest, TailoredDocumentResponse

router = APIRouter()


@router.post("/generate", response_model=ResponseModel[dict])
async def generate_material(payload: MaterialGenerateRequest, db: AsyncSession = Depends(get_db)):
    # Trigger material generation background task
    return ResponseModel(
        message="Material generation task enqueued",
        data={
            "task_id": "task_mat_gen_456",
            "job_id": payload.job_id,
            "doc_type": payload.doc_type,
            "status": "queued"
        }
    )


@router.get("/job/{job_id}", response_model=ResponseModel[List[TailoredDocumentResponse]])
async def get_materials_for_job(job_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TailoredDocument).where(TailoredDocument.job_id == job_id))
    docs = result.scalars().all()
    return ResponseModel(data=list(docs))
