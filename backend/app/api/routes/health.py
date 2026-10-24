import shutil
import shutil
from pathlib import Path
from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()

@router.get("/health")
def get_health():
    """Check API readiness and status of dependencies."""
    # Check disk storage
    storage_ok = settings.TEMP_DIR.exists() and settings.STORAGE_PATH.exists()
    
    # Check system binaries
    binaries = {
        "ghostscript": bool(settings.GHOSTSCRIPT_PATH or shutil.which("gs") or shutil.which("gswin64c")),
        "tesseract": bool(settings.TESSERACT_PATH or shutil.which("tesseract")),
        "libreoffice": bool(settings.LIBREOFFICE_PATH or shutil.which("soffice") or shutil.which("libreoffice")),
        "qpdf": bool(settings.QPDF_PATH or shutil.which("qpdf")),
    }
    
    # Python-based document engines (always available)
    built_in_engines = {
        "pypdf": True,
        "pymupdf": True,
        "pikepdf": True,
        "pdfplumber": True,
        "python_docx": True,
        "python_pptx": True,
        "openpyxl": True,
        "reportlab": True,
        "pymupdf4llm": True
    }
    
    return {
        "status": "healthy",
        "brand": settings.BRAND_NAME,
        "environment": settings.APP_ENV,
        "storage_ready": storage_ok,
        "system_binaries": binaries,
        "built_in_engines": built_in_engines,
        "ai_integration": {
            "provider": settings.AI_PROVIDER,
            "configured": bool(settings.OPENAI_API_KEY or settings.GEMINI_API_KEY or settings.ANTHROPIC_API_KEY)
        }
    }
