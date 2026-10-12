from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.schemas.analytics import (
    DashboardStatsResponse,
    TokenUsageResponse,
)

router = APIRouter()

DB = Depends(get_db)


@router.get("/dashboard")
async def get_dashboard_analytics(db: AsyncSession = DB):
    """Get high-level dashboard metrics: total jobs discovered, fit scored, reviewed, applied, skipped, and failed."""
    pass


@router.get("/tokens")
async def get_token_usage_analytics(db: AsyncSession = DB):
    """Get telemetry breakdown of LLM token consumption and estimated dollar costs per provider and task type."""
    pass


@router.get("/export/excel")
async def export_applications_excel(db: AsyncSession = DB):
    """Export complete application history and outcomes into an Excel workbook (.xlsx)."""
    pass


@router.get("/export/csv")
async def export_applications_csv(db: AsyncSession = DB):
    """Export complete application history and outcomes into CSV format."""
    pass
