import os
import zipfile
from pathlib import Path
from typing import List, Dict, Any, Tuple
import pypdf
import pymupdf  # fitz
from PIL import Image

from app.core.errors import InvalidFileException, ProcessingException

def parse_page_ranges(range_str: str, total_pages: int) -> List[int]:
    """Parse string like '1-3, 5, 7-10' into 1-indexed list of page numbers."""
    pages = []
    parts = [p.strip() for p in range_str.split(",") if p.strip()]
    if not parts:
        raise InvalidFileException("No page ranges specified.")
        
    for part in parts:
        if "-" in part:
            sub = part.split("-")
            if len(sub) != 2:
                raise InvalidFileException(f"Invalid range syntax: '{part}'")
            try:
                start = int(sub[0].strip())
                end = int(sub[1].strip())
            except ValueError:
                raise InvalidFileException(f"Invalid numbers in range: '{part}'")
            if start < 1 or end < 1:
                raise InvalidFileException("Page numbers must be 1 or greater.")
            if start > total_pages or end > total_pages:
                raise InvalidFileException(f"Range {start}-{end} exceeds total pages ({total_pages}).")
            if start > end:
                step = -1
            else:
                step = 1
            for p in range(start, end + step, step):
                pages.append(p)
        else:
            try:
                p = int(part)
            except ValueError:
                raise InvalidFileException(f"Invalid page number: '{part}'")
            if p < 1 or p > total_pages:
                raise InvalidFileException(f"Page {p} is out of bounds (1-{total_pages}).")
            pages.append(p)
            
    return pages

def merge_pdfs(input_paths: List[Path], output_path: Path) -> Dict[str, Any]:
    """Merge multiple PDF files in order."""
    if not input_paths:
        raise InvalidFileException("No PDF files provided for merging.")
        
    doc_out = pymupdf.open()
    total_pages = 0
    
    try:
        for p in input_paths:
            if not p.exists() or p.stat().st_size == 0:
                raise InvalidFileException(f"File {p.name} is missing or empty.")
            try:
                doc_in = pymupdf.open(str(p))
                if doc_in.is_encrypted:
                    raise InvalidFileException(f"File {p.name} is password protected. Unlock it first.")
                doc_out.insert_pdf(doc_in)
                total_pages += len(doc_in)
                doc_in.close()
            except Exception as e:
                raise ProcessingException(f"Failed to read {p.name}: {str(e)}")
                
        if total_pages == 0:
            raise ProcessingException("Combined document contains 0 pages.")
            
        doc_out.save(str(output_path), garbage=4, deflate=True)
        doc_out.close()
        
        return {
            "page_count": total_pages,
            "output_size": output_path.stat().st_size
        }
    except Exception:
        doc_out.close()
        raise

def split_pdf(input_path: Path, output_dir: Path, mode: str, ranges: str = "1", group_size: int = 1) -> List[Path]:
    """Split PDF into multiple files according to mode."""
    if not input_path.exists():
        raise InvalidFileException("Input PDF not found.")
        
    doc = pymupdf.open(str(input_path))
    if doc.is_encrypted:
        doc.close()
        raise InvalidFileException("Input PDF is encrypted. Unlock it first.")
        
    total_pages = len(doc)
    if total_pages == 0:
        doc.close()
        raise ProcessingException("PDF contains no pages.")
        
    created_files: List[Path] = []
    base_name = input_path.stem
    
    if mode == "ranges":
        selected_pages = parse_page_ranges(ranges, total_pages)
        out_doc = pymupdf.open()
        for p in selected_pages:
            out_doc.insert_pdf(doc, from_page=p - 1, to_page=p - 1)
        out_file = output_dir / f"{base_name}_split.pdf"
        out_doc.save(str(out_file), garbage=4, deflate=True)
        out_doc.close()
        created_files.append(out_file)
        
    elif mode == "extract_all":
        for i in range(total_pages):
            out_doc = pymupdf.open()
            out_doc.insert_pdf(doc, from_page=i, to_page=i)
            out_file = output_dir / f"{base_name}_page_{i + 1:03d}.pdf"
            out_doc.save(str(out_file), garbage=4, deflate=True)
            out_doc.close()
            created_files.append(out_file)
            
    elif mode == "fixed_groups":
        if group_size < 1:
            group_size = 1
        part_idx = 1
        for start_idx in range(0, total_pages, group_size):
            end_idx = min(start_idx + group_size - 1, total_pages - 1)
            out_doc = pymupdf.open()
            out_doc.insert_pdf(doc, from_page=start_idx, to_page=end_idx)
            out_file = output_dir / f"{base_name}_part_{part_idx:02d}_pages_{start_idx + 1}-{end_idx + 1}.pdf"
            out_doc.save(str(out_file), garbage=4, deflate=True)
            out_doc.close()
            created_files.append(out_file)
            part_idx += 1
    else:
        doc.close()
        raise InvalidFileException(f"Unknown split mode '{mode}'.")
        
    doc.close()
    
    # If multiple files created, also bundle into a ZIP archive for convenience
    if len(created_files) > 1:
        zip_path = output_dir / f"{base_name}_split_all.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
            for f in created_files:
                z.write(f, arcname=f.name)
        created_files.insert(0, zip_path)
        
    return created_files

def remove_pages(input_path: Path, output_path: Path, pages_to_remove: List[int]) -> Dict[str, Any]:
    """Delete selected 1-indexed pages from a PDF."""
    doc = pymupdf.open(str(input_path))
    if doc.is_encrypted:
        doc.close()
        raise InvalidFileException("Input PDF is encrypted.")
        
    total_pages = len(doc)
    remove_set = set(pages_to_remove)
    
    # Validate bounds
    for p in remove_set:
        if p < 1 or p > total_pages:
            doc.close()
            raise InvalidFileException(f"Page {p} is out of bounds (1-{total_pages}).")
            
    pages_to_keep = [i for i in range(1, total_pages + 1) if i not in remove_set]
    if not pages_to_keep:
        doc.close()
        raise InvalidFileException("Cannot remove all pages. At least 1 page must remain.")
        
    out_doc = pymupdf.open()
    for p in pages_to_keep:
        out_doc.insert_pdf(doc, from_page=p - 1, to_page=p - 1)
        
    out_doc.save(str(output_path), garbage=4, deflate=True)
    out_doc.close()
    doc.close()
    
    return {
        "original_page_count": total_pages,
        "removed_pages_count": len(remove_set),
        "resulting_page_count": len(pages_to_keep),
        "output_size": output_path.stat().st_size
    }

def extract_pages(input_path: Path, output_dir: Path, pages_to_extract: List[int], as_single_pdf: bool = True) -> List[Path]:
    """Extract specified 1-indexed pages."""
    doc = pymupdf.open(str(input_path))
    if doc.is_encrypted:
        doc.close()
        raise InvalidFileException("Input PDF is encrypted.")
        
    total = len(doc)
    if not pages_to_extract:
        doc.close()
        raise InvalidFileException("No pages specified to extract.")
        
    for p in pages_to_extract:
        if p < 1 or p > total:
            doc.close()
            raise InvalidFileException(f"Page {p} is out of bounds (1-{total}).")
            
    created_files: List[Path] = []
    base_name = input_path.stem
    
    if as_single_pdf:
        out_doc = pymupdf.open()
        for p in pages_to_extract:
            out_doc.insert_pdf(doc, from_page=p - 1, to_page=p - 1)
        out_path = output_dir / f"{base_name}_extracted.pdf"
        out_doc.save(str(out_path), garbage=4, deflate=True)
        out_doc.close()
        created_files.append(out_path)
    else:
        for idx, p in enumerate(pages_to_extract):
            out_doc = pymupdf.open()
            out_doc.insert_pdf(doc, from_page=p - 1, to_page=p - 1)
            out_path = output_dir / f"{base_name}_extracted_p{p}_{idx + 1}.pdf"
            out_doc.save(str(out_path), garbage=4, deflate=True)
            out_doc.close()
            created_files.append(out_path)
            
        if len(created_files) > 1:
            zip_path = output_dir / f"{base_name}_extracted_pages.zip"
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
                for f in created_files:
                    z.write(f, arcname=f.name)
            created_files.insert(0, zip_path)
            
    doc.close()
    return created_files

def organize_pdf(input_path: Path, output_path: Path, actions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Reorder, duplicate, rotate, and delete pages according to user instructions."""
    doc = pymupdf.open(str(input_path))
    if doc.is_encrypted:
        doc.close()
        raise InvalidFileException("Input PDF is encrypted.")
        
    total = len(doc)
    out_doc = pymupdf.open()
    
    for item in actions:
        if item.get("deleted", False):
            continue
        p = item.get("page_num", 1)
        if p < 1 or p > total:
            continue
        rot = item.get("rotation", 0) % 360
        count = max(1, item.get("duplicate_count", 1))
        
        for _ in range(count):
            new_page_idx = len(out_doc)
            out_doc.insert_pdf(doc, from_page=p - 1, to_page=p - 1)
            if rot != 0:
                page = out_doc[new_page_idx]
                page.set_rotation((page.rotation + rot) % 360)
                
    if len(out_doc) == 0:
        doc.close()
        out_doc.close()
        raise InvalidFileException("Resulting PDF would have 0 pages.")
        
    out_doc.save(str(output_path), garbage=4, deflate=True)
    page_count = len(out_doc)
    out_doc.close()
    doc.close()
    
    return {
        "page_count": page_count,
        "output_size": output_path.stat().st_size
    }

def scan_to_pdf(image_paths: List[Path], output_path: Path, page_size: str = "A4", orientation: str = "portrait", auto_rotate: bool = True) -> Dict[str, Any]:
    """Convert scanned images/photos into an organized multi-page PDF."""
    if not image_paths:
        raise InvalidFileException("No images provided.")
        
    doc = pymupdf.open()
    
    # Dimensions in points (72 points/inch)
    standard_sizes = {
        "A4": (595, 842),
        "Letter": (612, 792),
    }
    
    for img_path in image_paths:
        try:
            with Image.open(str(img_path)) as pil_img:
                w, h = pil_img.size
                
                # Check orientation
                if page_size in standard_sizes:
                    sw, sh = standard_sizes[page_size]
                    if orientation == "landscape":
                        target_w, target_h = max(sw, sh), min(sw, sh)
                    else:
                        target_w, target_h = min(sw, sh), max(sw, sh)
                else:
                    # Fit to image
                    target_w, target_h = float(w), float(h)
                    
                page = doc.new_page(width=target_w, height=target_h)
                
                # Calculate fit rectangle maintaining aspect ratio
                aspect = w / h
                target_aspect = target_w / target_h
                
                if aspect > target_aspect:
                    # Wider
                    rw = target_w - 40
                    rh = rw / aspect
                else:
                    rh = target_h - 40
                    rw = rh * aspect
                    
                rx = (target_w - rw) / 2
                ry = (target_h - rh) / 2
                rect = pymupdf.Rect(rx, ry, rx + rw, ry + rh)
                
                page.insert_image(rect, filename=str(img_path))
        except Exception as e:
            raise ProcessingException(f"Failed to process image {img_path.name}: {str(e)}")
            
    doc.save(str(output_path), garbage=4, deflate=True)
    page_count = len(doc)
    doc.close()
    
    return {
        "page_count": page_count,
        "output_size": output_path.stat().st_size
    }
