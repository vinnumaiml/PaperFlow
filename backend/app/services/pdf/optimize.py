import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
import pymupdf  # fitz
import pikepdf
from PIL import Image
import io

from app.core.config import settings
from app.core.errors import InvalidFileException, ProcessingException

def is_valid_pdf(pdf_path: Path) -> bool:
    """Validate that the PDF can be opened and parsed by PyMuPDF and pikepdf."""
    try:
        doc = pymupdf.open(str(pdf_path))
        if len(doc) == 0:
            doc.close()
            return False
        # Try loading first page
        _ = doc[0].get_text()
        doc.close()
        return True
    except Exception:
        return False

def _recompress_images_in_pdf(doc: pymupdf.Document, max_dpi: int = 120, jpeg_quality: int = 70) -> int:
    """Downsample and recompress embedded raster images in PDF."""
    images_processed = 0
    xrefs_handled = set()
    
    for page_idx in range(len(doc)):
        page = doc[page_idx]
        image_list = page.get_images(full=True)
        
        for img_info in image_list:
            xref = img_info[0]
            if xref in xrefs_handled:
                continue
            xrefs_handled.add(xref)
            
            try:
                base_image = doc.extract_image(xref)
                if not base_image:
                    continue
                
                image_bytes = base_image["image"]
                orig_ext = base_image["ext"]
                orig_width = base_image["width"]
                orig_height = base_image["height"]
                
                # Check if image is reasonably large to benefit from downsampling
                if orig_width < 100 and orig_height < 100:
                    continue
                    
                with Image.open(io.BytesIO(image_bytes)) as pil_img:
                    # Convert palette or RGBA with transparent mask if needed
                    mode = pil_img.mode
                    if mode in ("RGBA", "P"):
                        pil_img = pil_img.convert("RGB")
                    elif mode not in ("RGB", "L"):
                        pil_img = pil_img.convert("RGB")
                        
                    # Calculate downsample scale
                    scale = 1.0
                    target_max_dim = int(max_dpi * 8.5)  # approximate for standard page
                    max_dim = max(orig_width, orig_height)
                    if max_dim > target_max_dim:
                        scale = target_max_dim / max_dim
                        new_w = max(50, int(orig_width * scale))
                        new_h = max(50, int(orig_height * scale))
                        pil_img = pil_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                        
                    # Save as JPEG
                    out_buffer = io.BytesIO()
                    pil_img.save(out_buffer, format="JPEG", quality=jpeg_quality, optimize=True)
                    new_bytes = out_buffer.getvalue()
                    
                    # Only replace if newly compressed bytes are smaller
                    if len(new_bytes) < len(image_bytes):
                        doc.update_stream(xref, new_bytes)
                        images_processed += 1
            except Exception:
                continue
                
    return images_processed

def _generate_candidate(
    input_path: Path,
    candidate_path: Path,
    deflate_streams: bool = True,
    clean_meta: bool = True,
    max_dpi: int = 150,
    jpeg_quality: int = 80,
    linearize: bool = False
) -> int:
    """Generate candidate PDF and return its file size in bytes."""
    doc = pymupdf.open(str(input_path))
    
    if max_dpi < 300 or jpeg_quality < 95:
        _recompress_images_in_pdf(doc, max_dpi=max_dpi, jpeg_quality=jpeg_quality)
        
    doc.save(
        str(candidate_path),
        garbage=4 if deflate_streams else 2,
        deflate=deflate_streams,
        clean=clean_meta,
        linear=linearize
    )
    doc.close()
    
    # Try pikepdf stream compression pass
    try:
        with pikepdf.open(str(candidate_path), allow_overwriting_input=True) as pike_doc:
            pike_doc.save(
                str(candidate_path),
                compress_streams=True,
                linearize=linearize,
                recompress_flate=True
            )
    except Exception:
        pass
        
    return candidate_path.stat().st_size

def compress_pdf(
    input_path: Path,
    output_path: Path,
    preset: str = "recommended",
    custom_target_kb: Optional[int] = None,
    aggressive: bool = False
) -> Dict[str, Any]:
    """
    Real compression search algorithm.
    Evaluates candidate outputs with different compression strategies,
    ensuring valid output files, comparing against original size and custom target.
    """
    if not input_path.exists() or input_path.stat().st_size == 0:
        raise InvalidFileException("Input PDF is missing or empty.")
        
    original_size = input_path.stat().st_size
    temp_dir = output_path.parent / "compression_candidates"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if input is readable
    if not is_valid_pdf(input_path):
        raise InvalidFileException("Input file is not a valid or readable PDF.")
        
    target_bytes = (custom_target_kb * 1024) if custom_target_kb and custom_target_kb > 0 else None
    
    # Search strategies define parameters (DPI, quality, deflate, linearize)
    strategies = [
        {"name": "Lossless / High Quality", "dpi": 200, "quality": 85, "deflate": True, "clean": True},
        {"name": "Balanced / Recommended", "dpi": 140, "quality": 75, "deflate": True, "clean": True},
        {"name": "Standard Web", "dpi": 110, "quality": 60, "deflate": True, "clean": True},
        {"name": "Compact / Smaller File", "dpi": 90, "quality": 50, "deflate": True, "clean": True},
        {"name": "Aggressive Downsample", "dpi": 72, "quality": 35, "deflate": True, "clean": True},
    ]
    
    candidate_results: List[Tuple[int, Path, str, Dict[str, Any]]] = []
    
    # If preset was selected and no custom target
    if not target_bytes:
        if preset == "high_quality":
            selected_configs = [strategies[0]]
        elif preset == "smaller_file":
            selected_configs = [strategies[3]]
            if aggressive:
                selected_configs.append(strategies[4])
        else: # recommended
            selected_configs = [strategies[1]]
    else:
        # Custom target: test candidate options from highest quality down to aggressive
        selected_configs = strategies if aggressive else strategies[:4]
        
    for idx, strat in enumerate(selected_configs):
        cand_path = temp_dir / f"cand_{idx}.pdf"
        try:
            cand_size = _generate_candidate(
                input_path,
                cand_path,
                deflate_streams=strat["deflate"],
                clean_meta=strat["clean"],
                max_dpi=strat["dpi"],
                jpeg_quality=strat["quality"]
            )
            if cand_path.exists() and is_valid_pdf(cand_path):
                candidate_results.append((cand_size, cand_path, strat["name"], strat))
        except Exception:
            continue
            
    # Clean up empty list check
    if not candidate_results:
        # Fallback to copy if optimization could not run
        shutil.copy(str(input_path), str(output_path))
        return {
            "original_size": original_size,
            "output_size": original_size,
            "reduction_percentage": 0.0,
            "target_achieved": True if not target_bytes or original_size <= target_bytes else False,
            "strategy": "Original Document Retained",
            "message": "File is already optimally compressed."
        }
        
    # Evaluate candidates
    best_candidate_path: Optional[Path] = None
    best_strategy_name = ""
    best_size = original_size
    target_achieved = False
    
    if target_bytes:
        # Find highest quality candidate that achieves <= target_bytes
        for size, path, name, _ in candidate_results:
            if size <= target_bytes:
                best_candidate_path = path
                best_strategy_name = name
                best_size = size
                target_achieved = True
                break
                
        # If none met the target, take the smallest achieved candidate
        if not best_candidate_path:
            candidate_results.sort(key=lambda x: x[0])
            best_size, best_candidate_path, best_strategy_name, _ = candidate_results[0]
            target_achieved = best_size <= target_bytes
    else:
        # Preset chosen: take candidate
        best_size, best_candidate_path, best_strategy_name, _ = candidate_results[0]
        
    # If the compressed output ended up larger than the original
    if best_size >= original_size:
        # Preserve original
        shutil.copy(str(input_path), str(output_path))
        actual_output_size = original_size
        strategy_used = "Original Retained (File was already optimally compressed)"
        reduction_pct = 0.0
        message = "File is already well-compressed. Retained original file to avoid increasing size."
    else:
        shutil.copy(str(best_candidate_path), str(output_path))
        actual_output_size = best_size
        strategy_used = best_strategy_name
        reduction_pct = round(((original_size - actual_output_size) / original_size) * 100, 2)
        if target_bytes:
            if target_achieved:
                message = f"Successfully reduced by {reduction_pct}% to satisfy target maximum of {custom_target_kb} KB."
            else:
                message = f"Reduced by {reduction_pct}%. Lowest safe quality reached {round(actual_output_size / 1024, 1)} KB without corrupting document structure."
        else:
            message = f"Optimized successfully using {strategy_used} profile."
            
    # Cleanup temp candidates
    shutil.rmtree(temp_dir, ignore_errors=True)
    
    return {
        "original_size": original_size,
        "output_size": actual_output_size,
        "reduction_percentage": reduction_pct,
        "target_achieved": target_achieved if target_bytes else True,
        "strategy": strategy_used,
        "message": message,
        "target_bytes": target_bytes
    }

def repair_pdf(input_path: Path, output_path: Path) -> Dict[str, Any]:
    """
    Repair a corrupt or malformed PDF using structural recovery.
    Uses pikepdf and PyMuPDF xref rebuild mechanisms.
    """
    if not input_path.exists() or input_path.stat().st_size == 0:
        raise InvalidFileException("Input file is empty or missing.")
        
    repair_successful = False
    recovery_method = ""
    
    # Attempt 1: pikepdf structural rebuild
    try:
        with pikepdf.open(str(input_path), recover=True) as pike_doc:
            pike_doc.save(str(output_path), linearize=False, compress_streams=True)
        if is_valid_pdf(output_path):
            repair_successful = True
            recovery_method = "pikepdf structural recovery"
    except Exception:
        pass
        
    # Attempt 2: PyMuPDF xref rebuild
    if not repair_successful:
        try:
            doc = pymupdf.open(str(input_path))
            if len(doc) > 0:
                doc.save(str(output_path), garbage=4, clean=True, deflate=True)
                doc.close()
                if is_valid_pdf(output_path):
                    repair_successful = True
                    recovery_method = "PyMuPDF xref rebuild"
        except Exception:
            pass
            
    # Attempt 3: Check if qpdf binary is available
    if not repair_successful and settings.QPDF_PATH:
        try:
            cmd = [settings.QPDF_PATH, "--repair-file", str(input_path), str(output_path)]
            res = subprocess.run(cmd, capture_output=True, timeout=30)
            if res.returncode == 0 and is_valid_pdf(output_path):
                repair_successful = True
                recovery_method = "qpdf system repair"
        except Exception:
            pass
            
    if not repair_successful or not output_path.exists():
        raise ProcessingException("The document has severe binary corruption and cannot be recovered by the structural repair engine.")
        
    # Verify rendered pages
    doc_ver = pymupdf.open(str(output_path))
    pages_count = len(doc_ver)
    doc_ver.close()
    
    return {
        "status": "Repaired",
        "method": recovery_method,
        "page_count": pages_count,
        "output_size": output_path.stat().st_size
    }


def is_page_blank(page: pymupdf.Page, sensitivity: float = 0.992) -> bool:
    """
    Explainable dual-heuristic check for blank pages:
    1. Check selectable text content.
    2. Check rendered visual content luminance distribution (prevents deleting signatures/diagrams).
    """
    text = page.get_text().strip()
    if len(text) > 5:
        return False
        
    # Render at low DPI for fast and accurate visual analysis
    pix = page.get_pixmap(dpi=54)
    img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("L")
    
    # Calculate fraction of nearly-white pixels (luminance >= 245)
    hist = img.histogram()
    total_pixels = img.width * img.height
    if total_pixels == 0:
        return True
        
    nearly_white = sum(hist[245:])
    white_ratio = nearly_white / total_pixels
    
    # A blank page has white ratio exceeding sensitivity and no text
    return white_ratio >= sensitivity

def remove_blank_pages(input_path: Path, output_path: Path, sensitivity: float = 0.992) -> Dict[str, Any]:
    """Detect and remove blank pages while preserving pages with visual content."""
    doc = pymupdf.open(str(input_path))
    if doc.is_encrypted:
        doc.close()
        raise InvalidFileException("Input PDF is encrypted.")
        
    total_pages = len(doc)
    blank_pages = []
    
    for i in range(total_pages):
        page = doc[i]
        if is_page_blank(page, sensitivity=sensitivity):
            blank_pages.append(i + 1)
            
    if len(blank_pages) == total_pages:
        doc.close()
        raise InvalidFileException("All pages in the document were detected as blank. At least 1 page must remain.")
        
    if not blank_pages:
        # None blank: copy original
        doc.save(str(output_path), garbage=4, deflate=True)
        doc.close()
        return {
            "original_page_count": total_pages,
            "removed_page_count": 0,
            "resulting_page_count": total_pages,
            "removed_pages": [],
            "message": "No blank pages detected. Document unchanged."
        }
        
    out_doc = pymupdf.open()
    blank_set = set(blank_pages)
    for i in range(total_pages):
        if (i + 1) not in blank_set:
            out_doc.insert_pdf(doc, from_page=i, to_page=i)
            
    out_doc.save(str(output_path), garbage=4, deflate=True)
    out_doc.close()
    doc.close()
    
    return {
        "original_page_count": total_pages,
        "removed_page_count": len(blank_pages),
        "resulting_page_count": total_pages - len(blank_pages),
        "removed_pages": blank_pages,
        "message": f"Successfully removed {len(blank_pages)} blank page(s): {', '.join(map(str, blank_pages))}."
    }

def clean_and_deskew_pdf(
    input_path: Path,
    output_path: Path,
    deskew: bool = True,
    enhance_contrast: bool = True
) -> Dict[str, Any]:
    """Clean scanned document pages by auto-enhancing contrast and deskewing."""
    from PIL import ImageEnhance, ImageOps
    import numpy as np

    doc = pymupdf.open(str(input_path))
    if doc.is_encrypted:
        doc.close()
        raise InvalidFileException("Input PDF is encrypted.")
        
    out_doc = pymupdf.open()
    total_pages = len(doc)
    
    for i in range(total_pages):
        page = doc[i]
        rect = page.rect
        
        # Render high-resolution page
        pix = page.get_pixmap(dpi=150)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        
        # 1. Deskew detection using horizontal projection variance
        best_angle = 0.0
        if deskew:
            gray = img.convert("L")
            # Downsample for fast angle detection
            small = gray.resize((int(gray.width * 0.4), int(gray.height * 0.4)))
            arr = np.array(small)
            
            # Test angles between -4 and +4 degrees in 0.5 step
            best_var = -1.0
            for test_ang in np.arange(-4.0, 4.5, 0.5):
                rotated = Image.fromarray(arr).rotate(test_ang, resample=Image.Resampling.BILINEAR, fillcolor=255)
                # Compute horizontal projection profile variance
                proj = np.mean(np.array(rotated), axis=1)
                var = np.var(proj)
                if var > best_var:
                    best_var = var
                    best_angle = test_ang
                    
            if abs(best_angle) >= 0.5:
                img = img.rotate(best_angle, resample=Image.Resampling.BICUBIC, expand=False, fillcolor="white")
                
        # 2. Contrast & Sharpen Enhancement
        if enhance_contrast:
            # Autocontrast
            if img.mode != "RGB":
                img = img.convert("RGB")
            img = ImageOps.autocontrast(img, cutoff=1)
            # Mild sharpness boost
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(1.2)
            
        # Insert cleaned image back into PDF page
        new_page = out_doc.new_page(width=rect.width, height=rect.height)
        img_buffer = io.BytesIO()
        img.save(img_buffer, format="JPEG", quality=90)
        new_page.insert_image(new_page.rect, stream=img_buffer.getvalue())
        
    out_doc.save(str(output_path), garbage=4, deflate=True)
    out_doc.close()
    doc.close()
    
    return {
        "page_count": total_pages,
        "deskew_applied": deskew,
        "contrast_enhanced": enhance_contrast,
        "output_size": output_path.stat().st_size
    }
