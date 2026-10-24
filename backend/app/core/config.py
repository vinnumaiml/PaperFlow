import os
from pathlib import Path
from typing import List
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ROOT_DIR = BASE_DIR.parent

class Settings(BaseModel):
    BRAND_NAME: str = os.getenv("BRAND_NAME", "PaperFlow")
    APP_ENV: str = os.getenv("APP_ENV", "development")
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    
    ALLOWED_ORIGINS: List[str] = [
        origin.strip()
        for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000,*").split(",")
        if origin.strip()
    ]
    
    STORAGE_PATH: Path = Path(os.getenv("STORAGE_PATH", str(BASE_DIR / "data" / "storage"))).resolve()
    TEMP_DIR: Path = Path(os.getenv("TEMP_DIR", str(BASE_DIR / "data" / "temp"))).resolve()
    
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
    MAX_BATCH_FILES: int = int(os.getenv("MAX_BATCH_FILES", "30"))
    JOB_RETENTION_MINUTES: int = int(os.getenv("JOB_RETENTION_MINUTES", "60"))
    CLEANUP_INTERVAL_MINUTES: int = int(os.getenv("CLEANUP_INTERVAL_MINUTES", "15"))
    
    # System binary paths
    GHOSTSCRIPT_PATH: str = os.getenv("GHOSTSCRIPT_PATH", "")
    TESSERACT_PATH: str = os.getenv("TESSERACT_PATH", "")
    LIBREOFFICE_PATH: str = os.getenv("LIBREOFFICE_PATH", "")
    QPDF_PATH: str = os.getenv("QPDF_PATH", "")
    
    # AI Providers
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "openai")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-paperflow-2026")
    ENABLE_CORS: bool = os.getenv("ENABLE_CORS", "true").lower() in ("true", "1", "yes")

settings = Settings()

# Ensure directories exist
settings.STORAGE_PATH.mkdir(parents=True, exist_ok=True)
settings.TEMP_DIR.mkdir(parents=True, exist_ok=True)
