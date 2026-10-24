import uuid
import time
import asyncio
from typing import Dict, Optional, Any, Callable
from datetime import datetime, timezone

from app.schemas.job import JobStatus, JobResponse, JobProgress, OutputFile
from app.services.storage import storage_service
from app.core.errors import JobNotFoundException

class JobsManager:
    def __init__(self):
        self._jobs: Dict[str, dict] = {}
        self._tasks: Dict[str, asyncio.Task] = {}

    def create_job(self, tool: str, file_count: int = 1) -> str:
        job_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        self._jobs[job_id] = {
            "id": job_id,
            "tool": tool,
            "status": JobStatus.QUEUED,
            "progress": JobProgress(step="Queued", percentage=0, message="Job is in queue").model_dump(),
            "created_at": now,
            "updated_at": now,
            "files_count": file_count,
            "outputs": [],
            "error": None,
            "stats": {},
            "start_time": time.time(),
            "end_time": None
        }
        
        # Initialize job workspace on disk
        storage_service.create_job_workspace(job_id)
        return job_id

    def get_job(self, job_id: str) -> dict:
        if job_id not in self._jobs:
            raise JobNotFoundException(job_id)
        return self._jobs[job_id]

    def update_progress(self, job_id: str, step: str, percentage: int, message: str):
        if job_id in self._jobs:
            self._jobs[job_id]["progress"] = {
                "step": step,
                "percentage": max(0, min(100, percentage)),
                "message": message
            }
            self._jobs[job_id]["updated_at"] = datetime.now(timezone.utc).isoformat()

    def set_processing(self, job_id: str, message: str = "Processing document"):
        if job_id in self._jobs:
            self._jobs[job_id]["status"] = JobStatus.PROCESSING
            self.update_progress(job_id, "Processing", 15, message)

    def set_completed(self, job_id: str, outputs: list, stats: Optional[dict] = None):
        if job_id in self._jobs:
            job = self._jobs[job_id]
            job["status"] = JobStatus.COMPLETED
            job["outputs"] = outputs
            if stats:
                job["stats"] = stats
            job["end_time"] = time.time()
            job["execution_time_seconds"] = round(job["end_time"] - job["start_time"], 2)
            self.update_progress(job_id, "Done", 100, "Processing completed successfully.")

    def set_failed(self, job_id: str, error_message: str):
        if job_id in self._jobs:
            job = self._jobs[job_id]
            job["status"] = JobStatus.FAILED
            job["error"] = error_message
            job["end_time"] = time.time()
            job["execution_time_seconds"] = round(job["end_time"] - job["start_time"], 2)
            self.update_progress(job_id, "Failed", 100, f"Error: {error_message}")

    def cancel_job(self, job_id: str) -> bool:
        if job_id in self._tasks and not self._tasks[job_id].done():
            self._tasks[job_id].cancel()
        if job_id in self._jobs:
            self._jobs[job_id]["status"] = JobStatus.CANCELLED
            self.update_progress(job_id, "Cancelled", 0, "Job was cancelled by user.")
            storage_service.cleanup_job(job_id)
            return True
        return False

    def to_response(self, job_id: str) -> JobResponse:
        data = self.get_job(job_id)
        return JobResponse(
            id=data["id"],
            tool=data["tool"],
            status=data["status"],
            progress=JobProgress(**data["progress"]),
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            files_count=data.get("files_count", 1),
            outputs=[OutputFile(**o) for o in data.get("outputs", [])],
            error=data.get("error"),
            execution_time_seconds=data.get("execution_time_seconds"),
            stats=data.get("stats", {})
        )

    def run_async(self, job_id: str, coro_fn: Callable):
        async def runner():
            try:
                self.set_processing(job_id, "Starting task...")
                await coro_fn()
            except asyncio.CancelledError:
                self.cancel_job(job_id)
            except Exception as e:
                self.set_failed(job_id, str(e))
                
        task = asyncio.create_task(runner())
        self._tasks[job_id] = task

jobs_manager = JobsManager()
