from pathlib import Path
from typing import List, Dict, Any
from PIL import Image
import pymupdf  # fitz

from app.core.errors import InvalidFileException, ProcessingException

def images_to_pdf(
    image_paths: List[Path],
    output_path: Path,
    page_size: str = "A4",
    orientation: str = "portrait",
    margin: int = 20,
    fit_mode: str = "contain"
) -> Dict[str, Any]:
    """Convert multiple images (JPG, PNG, WebP) into a clean PDF."""
    if not image_paths:
        raise InvalidFileException("No images provided.")
        
    doc = pymupdf.open()
    
    standard_sizes = {
        "A4": (595.0, 842.0),
        "Letter": (612.0, 792.0),
    }
    
    for img_path in image_paths:
        if not img_path.exists():
            continue
        try:
            with Image.open(str(img_path)) as pil_img:
                w, h = pil_img.size
                
                if page_size in standard_sizes:
                    sw, sh = standard_sizes[page_size]
                    if orientation == "landscape":
                        pw, ph = max(sw, sh), min(sw, sh)
                    else:
                        pw, ph = min(sw, sh), max(sw, sh)
                else:
                    pw, ph = float(w), float(h)
                    
                page = doc.new_page(width=pw, height=ph)
                
                avail_w = max(10, pw - (margin * 2))
                avail_h = max(10, ph - (margin * 2))
                
                aspect = w / h
                avail_aspect = avail_w / avail_h
                
                if fit_mode == "fill":
                    target_w = avail_w
                    target_h = avail_h
                elif fit_mode == "original":
                    target_w = min(float(w), avail_w)
                    target_h = min(float(h), avail_h)
                else:  # contain
                    if aspect > avail_aspect:
                        target_w = avail_w
                        target_h = target_w / aspect
                    else:
                        target_h = avail_h
                        target_w = target_h * aspect
                        
                rx = (pw - target_w) / 2
                ry = (ph - target_h) / 2
                
                rect = pymupdf.Rect(rx, ry, rx + target_w, ry + target_h)
                page.insert_image(rect, filename=str(img_path))
        except Exception as e:
            raise ProcessingException(f"Failed to process image {img_path.name}: {str(e)}")
            
    if len(doc) == 0:
        doc.close()
        raise ProcessingException("No valid images could be converted.")
        
    doc.save(str(output_path), garbage=4, deflate=True)
    page_count = len(doc)
    doc.close()
    
    return {
        "page_count": page_count,
        "output_size": output_path.stat().st_size
    }
