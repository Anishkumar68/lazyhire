from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class ExecutionStartRequest(BaseModel):
    platform: str = "linkedin"  # linkedin, greenhouse, lever, ashby, workday, all
    headless: bool = False
    stop_before_submit: bool = True  # Dry run mode
    max_applications: int = 25
    click_gap_min: float = 1.5
    click_gap_max: float = 4.0
    profile_path: Optional[str] = None


class ExecutionStatusResponse(BaseModel):
    is_running: bool = False
    is_paused: bool = False
    platform: Optional[str] = None
    current_job_id: Optional[int] = None
    current_application_id: Optional[int] = None
    processed_count: int = 0
    success_count: int = 0
    failed_count: int = 0
    session_start_time: Optional[datetime] = None


class SessionHealthResponse(BaseModel):
    platform: str = "linkedin"
    browser_connected: bool = False
    is_logged_in: bool = False
    two_factor_required: bool = False
    cookies_valid: bool = False
    profile_dir: Optional[str] = None
    details: Optional[str] = None


class QuestionSolveRequest(BaseModel):
    question_text: str
    question_type: str = "text"  # text, radio, dropdown, checkbox
    options: Optional[List[str]] = None
    candidate_id: Optional[int] = None


class QuestionSolveResponse(BaseModel):
    question_text: str
    resolved_answer: str
    resolution_tier: str  # tier_1_heuristic, tier_2_memory_bank, tier_3_llm_fallback
    confidence: float = 1.0
    explanation: Optional[str] = None
