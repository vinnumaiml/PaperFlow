import os
import shutil
import time
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.config import settings
from app.core.security import sanitize_filename, validate_file_signature, is_safe_path
from app.core.errors import InvalidFileException, PaperFlowException

class StorageService:
    def __init__(self):
        self.base_temp = settings.TEMP_DIR
        self.base_storage = settings.STORAGE_PATH
        self.base_temp.mkdir(parents=True, exist_ok=True)
        self.base_storage.mkdir(parents=True, exist_ok=True)

    def get_job_dir(self, job_id: str) -> Path:
        job_dir = self.base_temp / job_id
        if not is_safe_path(self.base_temp, job_dir):
            raise PaperFlowException("Invalid job identifier path.")
        return job_dir

    def create_job_workspace(self, job_id: str) -> dict:
        job_dir = self.get_job_dir(job_id)
        inputs_dir = job_dir / "inputs"
        outputs_dir = job_dir / "outputs"
        
        inputs_dir.mkdir(parents=True, exist_ok=True)
        outputs_dir.mkdir(parents=True, exist_ok=True)
        
        return {
            "root": job_dir,
            "inputs": inputs_dir,
            "outputs": outputs_dir
        }

    def save_upload_file(self, job_id: str, filename: str, content: bytes) -> Path:
        # Check size
        size_mb = len(content) / (1024 * 1024)
        if size_mb > settings.MAX_FILE_SIZE_MB:
            raise InvalidFileException(f"File exceeds maximum allowed size of {settings.MAX_FILE_SIZE_MB}MB.")
        
        clean_name = sanitize_filename(filename)
        ext = os.path.splitext(clean_name)[1].lower().lstrip(".")
        
        # Validate magic signature
        is_valid, msg = validate_file_signature(content, ext)
        if not is_valid:
            raise InvalidFileException(f"{filename}: {msg}")
        
        workspace = self.create_job_workspace(job_id)
        target_path = workspace["inputs"] / clean_name
        
        # If file already exists with same name, suffix with counter
        counter = 1
        base_stem = target_path.stem
        while target_path.exists():
            target_path = workspace["inputs"] / f"{base_stem}_{counter}.{ext}"
            counter += 1
            
        with open(target_path, "wb") as f:
            f.write(content)
            
        return target_path

    def get_job_inputs(self, job_id: str) -> List[Path]:
        workspace = self.get_job_dir(job_id)
        inputs_dir = workspace / "inputs"
        if not inputs_dir.exists():
            return []
        return sorted([p for p in inputs_dir.iterdir() if p.is_file()])

    def get_job_outputs(self, job_id: str) -> List[Path]:
        workspace = self.get_job_dir(job_id)
        outputs_dir = workspace / "outputs"
        if not outputs_dir.exists():
            return []
        return sorted([p for p in outputs_dir.iterdir() if p.is_file()])

    def get_output_file(self, job_id: str, filename: str) -> Optional[Path]:
        workspace = self.get_job_dir(job_id)
        clean_name = sanitize_filename(filename)
        target = workspace / "outputs" / clean_name
        if target.exists() and target.is_file() and is_safe_path(workspace / "outputs", target):
            return target
        return None

    def cleanup_job(self, job_id: str) -> bool:
        try:
            job_dir = self.get_job_dir(job_id)
            if job_dir.exists():
                shutil.rmtree(job_dir, ignore_errors=True)
                return True
        except Exception:
            pass
        return False

    def cleanup_expired_jobs(self, max_age_minutes: Optional[int] = None) -> int:
        if max_age_minutes is None:
            max_age_minutes = settings.JOB_RETENTION_MINUTES
        
        threshold = time.time() - (max_age_minutes * 60)
        cleaned_count = 0
        
        try:
            for item in self.base_temp.iterdir():
                if item.is_dir():
                    try:
                        stat = item.stat()
                        if stat.st_mtime < threshold:
                            shutil.rmtree(item, ignore_errors=True)
                            cleaned_count += 1
                    except Exception:
                        continue
        except Exception:
            pass
        return cleaned_count

storage_service = StorageService()
