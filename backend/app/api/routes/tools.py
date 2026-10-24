import json
from pathlib import Path
from typing import List, Dict, Any
from fastapi import APIRouter, UploadFile, File, HTTPException, status
import pymupdf

from app.core.errors import InvalidFileException
from app.services.pdf.edit import get_form_fields

router = APIRouter()

@router.post("/tools/inspect-pdf")
async def inspect_pdf(file: UploadFile = File(...)):
    """Inspect PDF page count, dimensions, form fields, and encryption status."""
    content = await file.read()
    if not content:
        raise InvalidFileException("Uploaded file is empty.")
        
    try:
        doc = pymupdf.open("pdf", content)
        is_enc = doc.is_encrypted
        page_count = len(doc)
        pages_info = []
        
        if not is_enc:
            for idx in range(min(page_count, 100)):
                p = doc[idx]
                pages_info.append({
                    "page": idx + 1,
                    "width": p.rect.width,
                    "height": p.rect.height,
                    "rotation": p.rotation
                })
                
        # Form fields
        fields = []
        if not is_enc:
            for p_idx, page in enumerate(doc):
                for widget in page.widgets():
                    fields.append({
                        "page": p_idx + 1,
                        "name": widget.field_name,
                        "type": widget.field_type_string,
                        "value": widget.field_value or ""
                    })
                    
        meta = doc.metadata or {} if not is_enc else {}
        doc.close()
        return {
            "filename": file.filename,
            "size_bytes": len(content),
            "is_encrypted": is_enc,
            "page_count": page_count,
            "pages": pages_info,
            "form_fields": fields,
            "metadata": {
                "title": meta.get("title") or "",
                "author": meta.get("author") or "",
                "subject": meta.get("subject") or "",
                "keywords": meta.get("keywords") or "",
                "creator": meta.get("creator") or "",
                "producer": meta.get("producer") or "",
            }
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to inspect PDF: {str(e)}")
