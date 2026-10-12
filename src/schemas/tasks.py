from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str  # PENDING, STARTED, SUCCESS, FAILURE, RETRY, REVOKED
    queue: Optional[str] = None
    result: Optional[Any] = None
    error: Optional[str] = None


class QueueStatusResponse(BaseModel):
    queue_name: str
    active_tasks: int = 0
    scheduled_tasks: int = 0
    reserved_tasks: int = 0


class DLQTaskResponse(BaseModel):
    task_id: str
    queue: str
    failed_at: datetime
    retry_count: int = 0
    error_message: str
    payload: Optional[Dict[str, Any]] = None
