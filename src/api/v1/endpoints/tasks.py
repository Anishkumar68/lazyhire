from typing import Optional, List
from fastapi import APIRouter

from src.schemas.tasks import (
    TaskStatusResponse,
    QueueStatusResponse,
    DLQTaskResponse,
)

router = APIRouter()


@router.get("/queues")
async def get_queue_status():
    """Monitor status and throughput across Celery queues (search, materials, application, maintenance)."""
    pass


@router.get("/dlq")
async def get_dlq_tasks():
    """List failed and dead-lettered background tasks requiring inspection or retry."""
    pass


@router.post("/dlq/{task_id}/retry")
async def retry_dlq_task(task_id: str):
    """Re-enqueue a failed task from the Dead Letter Queue back to its original worker queue."""
    pass


@router.delete("/dlq/{task_id}")
async def discard_dlq_task(task_id: str):
    """Discard and remove a task permanently from the Dead Letter Queue."""
    pass


@router.post("/cleanup")
async def trigger_maintenance_cleanup():
    """Trigger background maintenance pipeline to prune temporary PDFs, stale browser screenshots, and quarantined artifacts."""
    pass


@router.get("/{task_id}")
async def get_task_status(task_id: str):
    """Poll status, progress percentage, and result of an asynchronous background task."""
    pass
