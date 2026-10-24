from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class JobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class OutputFile(BaseModel):
    filename: str
    size_bytes: int
    download_url: str
    mime_type: str = "application/pdf"
    metadata: Dict[str, Any] = Field(default_factory=dict)

class JobProgress(BaseModel):
    step: str = "Initializing"
    percentage: int = 0
    message: str = "Job is queued"

class JobResponse(BaseModel):
    id: str
    tool: str
    status: JobStatus
    progress: JobProgress
    created_at: str
    updated_at: str
    files_count: int = 1
    outputs: List[OutputFile] = Field(default_factory=list)
    error: Optional[str] = None
    execution_time_seconds: Optional[float] = None
    stats: Dict[str, Any] = Field(default_factory=dict)
