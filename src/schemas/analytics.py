from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class DashboardStatsResponse(BaseModel):
    total_jobs_discovered: int = 0
    total_matched_jobs: int = 0
    total_pending_review: int = 0
    total_applied: int = 0
    total_skipped: int = 0
    total_failed: int = 0
    success_rate_percentage: float = 0.0
    total_tokens_used: int = 0
    total_estimated_cost_usd: float = 0.0


class TokenUsageResponse(BaseModel):
    provider_name: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0
    requests_count: int = 0
