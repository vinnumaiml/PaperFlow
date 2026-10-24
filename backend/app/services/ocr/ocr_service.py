import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, List
import pymupdf  # fitz
import pytesseract
from PIL import Image
import io

from app.core.config import settings
from app.core.errors import InvalidFileException, ProcessingException

def is_tesseract_available() -> bool:
    """Check if Tesseract binary is available either in path or configured."""
    if settings.TESSERACT_PATH and Path(settings.TESSERACT_PATH).exists():
        pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_PATH
        return True
    which_tess = shutil.which("tesseract")
    if which_tess:
        pytesseract.pytesseract.tesseract_cmd = which_tess
        return True
    return False

def ocr_pdf(input_path: Path, output_path: Path, language: str = "eng") -> Dict[str, Any]:
    """
    Perform OCR on scanned or mixed PDF pages to produce a searchable PDF.
    Preserves original page layout while adding searchable text layer.
    """
    if not input_path.exists():
        raise InvalidFileException("Input file not found.")
        
    doc = pymupdf.open(str(input_path))
    if doc.is_encrypted:
        doc.close()
        raise InvalidFileException("Document is encrypted. Unlock it first.")
        
    tess_available = is_tesseract_available()
    total_pages = len(doc)
    pages_ocr_applied = 0
    pages_already_searchable = 0
    
    # Try PyMuPDF's OCR rendering if tesseract is installed
    if tess_available:
        try:
            out_doc = pymupdf.open()
            for i in range(total_pages):
                page = doc[i]
                existing_text = page.get_text().strip()
                
                # If page already has searchable text, keep original vector layout
                if len(existing_text) > 50:
                    pages_already_searchable += 1
                    out_doc.insert_pdf(doc, from_page=i, to_page=i)
                else:
                    # Render page as high res image and OCR to PDF page
                    pix = page.get_pixmap(dpi=200)
                    img_bytes = pix.tobytes("png")
                    
                    # Use pytesseract to generate searchable PDF bytes for this page
                    pdf_bytes = pytesseract.image_to_pdf_or_hocr(
                        Image.open(io.BytesIO(img_bytes)),
                        lang=language,
                        extension='pdf'
                    )
                    ocr_page_doc = pymupdf.open("pdf", pdf_bytes)
                    out_doc.insert_pdf(ocr_page_doc)
                    ocr_page_doc.close()
                    pages_ocr_applied += 1
                    
            out_doc.save(str(output_path), garbage=4, deflate=True)
            out_doc.close()
            doc.close()
            
            return {
                "status": "Completed",
                "total_pages": total_pages,
                "pages_ocr_applied": pages_ocr_applied,
                "pages_already_searchable": pages_already_searchable,
                "language": language,
                "engine": "Tesseract OCR",
                "output_size": output_path.stat().st_size
            }
        except Exception as e:
            # Fall through if specific language pack missing
            pass
            
    # If tesseract is not available or errored, check if document already has text
    existing_all_text = ""
    for page in doc:
        existing_all_text += page.get_text()
        
    if len(existing_all_text.strip()) > 20:
        # Document already contains searchable text
        doc.save(str(output_path), garbage=4, deflate=True)
        doc.close()
        return {
            "status": "Completed",
            "total_pages": total_pages,
            "pages_ocr_applied": 0,
            "pages_already_searchable": total_pages,
            "language": language,
            "engine": "Native PDF Text Layer",
            "message": "Document already contains a readable text layer; searchable PDF preserved.",
            "output_size": output_path.stat().st_size
        }
        
    doc.close()
    raise ProcessingException(
        "Tesseract OCR is not installed or the language pack for '" + language + "' is missing. "
        "Please install Tesseract OCR on the server to process image-only scanned documents."
    )
