import os
import math
from pathlib import Path
from typing import List, Dict, Any, Optional
import pymupdf  # fitz
import pypdf

from app.core.errors import InvalidFileException, ProcessingException

def rotate_pdf(input_path: Path, output_path: Path, angle: int = 90, pages: Optional[List[int]] = None) -> Dict[str, Any]:
    """Rotate specified pages or entire document by angle (90, 180, 270)."""
    doc = pymupdf.open(str(input_path))
    if doc.is_encrypted:
        doc.close()
        raise InvalidFileException("Document is encrypted. Unlock it first.")
        
    total = len(doc)
    selected_set = set(pages) if pages else set(range(1, total + 1))
    
    for p_num in selected_set:
        if 1 <= p_num <= total:
            page = doc[p_num - 1]
            page.set_rotation((page.rotation + angle) % 360)
            
    doc.save(str(output_path), garbage=4, deflate=True)
    doc.close()
    
    return {
        "page_count": total,
        "rotated_pages_count": len(selected_set),
        "angle": angle,
        "output_size": output_path.stat().st_size
    }

def add_page_numbers(
    input_path: Path,
    output_path: Path,
    position: str = "bottom-center",
    format_str: str = "Page {page} of {total}",
    font_size: int = 10,
    margin: int = 36,
    start_number: int = 1,
    omit_pages: Optional[List[int]] = None
) -> Dict[str, Any]:
    """Insert page numbers into PDF at specified position."""
    doc = pymupdf.open(str(input_path))
    if doc.is_encrypted:
        doc.close()
        raise InvalidFileException("Document is encrypted.")
        
    total_pages = len(doc)
    omit_set = set(omit_pages or [])
    
    current_num = start_number
    
    for i in range(total_pages):
        page_idx = i + 1
        page = doc[i]
        
        if page_idx in omit_set:
            continue
            
        rect = page.rect
        w = rect.width
        h = rect.height
        
        text = format_str.format(page=current_num, total=total_pages)
        current_num += 1
        
        # Determine (x, y) coordinates
        # pymupdf coordinates: (0,0) is top-left
        if position == "bottom-center":
            x = w / 2 - (len(text) * font_size * 0.25)
            y = h - margin
        elif position == "bottom-left":
            x = margin
            y = h - margin
        elif position == "bottom-right":
            x = w - margin - (len(text) * font_size * 0.5)
            y = h - margin
        elif position == "top-center":
            x = w / 2 - (len(text) * font_size * 0.25)
            y = margin + font_size
        elif position == "top-left":
            x = margin
            y = margin + font_size
        elif position == "top-right":
            x = w - margin - (len(text) * font_size * 0.5)
            y = margin + font_size
        else:
            x = w / 2
            y = h - margin
            
        point = pymupdf.Point(x, y)
        page.insert_text(point, text, fontsize=font_size, color=(0.2, 0.2, 0.2))
        
    doc.save(str(output_path), garbage=4, deflate=True)
    doc.close()
    
    return {
        "page_count": total_pages,
        "position": position,
        "format": format_str,
        "output_size": output_path.stat().st_size
    }

def add_watermark(
    input_path: Path,
    output_path: Path,
    watermark_type: str = "text",
    text: str = "CONFIDENTIAL",
    image_path: Optional[Path] = None,
    opacity: float = 0.3,
    rotation: int = 45,
    font_size: int = 48,
    position: str = "center",
    pages: Optional[List[int]] = None
) -> Dict[str, Any]:
    """Apply text or image watermark to PDF pages."""
    doc = pymupdf.open(str(input_path))
    if doc.is_encrypted:
        doc.close()
        raise InvalidFileException("Document is encrypted.")
        
    total_pages = len(doc)
    page_set = set(pages) if pages else set(range(1, total_pages + 1))
    
    for i in range(total_pages):
        page_idx = i + 1
        if page_idx not in page_set:
            continue
            
        page = doc[i]
        rect = page.rect
        
        if watermark_type == "text" and text:
            # Insert watermark text rotated
            cx = rect.width / 2
            cy = rect.height / 2
            
            # Using page.insert_text with morph or angle
            point = pymupdf.Point(cx - (len(text) * font_size * 0.2), cy)
            # Add watermark with gray color and opacity
            page.insert_text(
                point,
                text,
                fontsize=font_size,
                color=(0.5, 0.5, 0.5),
                rotate=rotation,
                overlay=True
            )
        elif watermark_type == "image" and image_path and image_path.exists():
            # Image watermark centered with opacity
            img_w = rect.width * 0.6
            img_h = rect.height * 0.4
            ix = (rect.width - img_w) / 2
            iy = (rect.height - img_h) / 2
            img_rect = pymupdf.Rect(ix, iy, ix + img_w, iy + img_h)
            page.insert_image(img_rect, filename=str(image_path), overlay=True)
            
    doc.save(str(output_path), garbage=4, deflate=True)
    doc.close()
    
    return {
        "page_count": total_pages,
        "watermarked_pages": len(page_set),
        "type": watermark_type,
        "output_size": output_path.stat().st_size
    }

def crop_pdf(
    input_path: Path,
    output_path: Path,
    x: float = 0.0,
    y: float = 0.0,
    width: float = 1.0,
    height: float = 1.0,
    pages: Optional[List[int]] = None
) -> Dict[str, Any]:
    """Crop PDF page bounding boxes."""
    doc = pymupdf.open(str(input_path))
    if doc.is_encrypted:
        doc.close()
        raise InvalidFileException("Document is encrypted.")
        
    total = len(doc)
    page_set = set(pages) if pages else set(range(1, total + 1))
    
    # Coordinates are normalized 0.0 to 1.0
    for i in range(total):
        if (i + 1) not in page_set:
            continue
        page = doc[i]
        rect = page.rect
        
        crop_x0 = rect.x0 + (x * rect.width)
        crop_y0 = rect.y0 + (y * rect.height)
        crop_x1 = crop_x0 + (width * rect.width)
        crop_y1 = crop_y0 + (height * rect.height)
        
        new_box = pymupdf.Rect(crop_x0, crop_y0, crop_x1, crop_y1)
        page.set_cropbox(new_box)
        
    doc.save(str(output_path), garbage=4, deflate=True)
    doc.close()
    
    return {
        "page_count": total,
        "cropped_pages": len(page_set),
        "output_size": output_path.stat().st_size
    }

def edit_pdf(input_path: Path, output_path: Path, annotations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Apply user annotations (text, rectangles, highlights, drawings) directly onto PDF canvas.
    """
    doc = pymupdf.open(str(input_path))
    if doc.is_encrypted:
        doc.close()
        raise InvalidFileException("Document is encrypted.")
        
    total = len(doc)
    
    for annot in annotations:
        p_num = annot.get("page", 1)
        if p_num < 1 or p_num > total:
            continue
            
        page = doc[p_num - 1]
        a_type = annot.get("type", "text")
        
        # Color parsing: "#RRGGBB" -> tuple (r,g,b) in 0..1
        color_hex = annot.get("color", "#000000").lstrip("#")
        try:
            if len(color_hex) == 6:
                r = int(color_hex[0:2], 16) / 255.0
                g = int(color_hex[2:4], 16) / 255.0
                b = int(color_hex[4:6], 16) / 255.0
                rgb = (r, g, b)
            else:
                rgb = (0, 0, 0)
        except Exception:
            rgb = (0, 0, 0)
            
        x = float(annot.get("x", 0))
        y = float(annot.get("y", 0))
        
        if a_type == "text":
            text_str = annot.get("text", "")
            fsize = int(annot.get("font_size", 14))
            point = pymupdf.Point(x, y + fsize)
            page.insert_text(point, text_str, fontsize=fsize, color=rgb)
            
        elif a_type in ("rect", "highlight"):
            w = float(annot.get("width", 100))
            h = float(annot.get("height", 30))
            box = pymupdf.Rect(x, y, x + w, y + h)
            if a_type == "highlight":
                page.draw_rect(box, color=rgb, fill=(1, 1, 0), fill_opacity=0.35)
            else:
                page.draw_rect(box, color=rgb, width=2)
                
        elif a_type == "freeline":
            points_list = annot.get("points", [])
            if len(points_list) >= 2:
                for idx in range(len(points_list) - 1):
                    p1 = pymupdf.Point(points_list[idx][0], points_list[idx][1])
                    p2 = pymupdf.Point(points_list[idx + 1][0], points_list[idx + 1][1])
                    page.draw_line(p1, p2, color=rgb, width=2)
                    
    doc.save(str(output_path), garbage=4, deflate=True)
    doc.close()
    
    return {
        "page_count": total,
        "annotations_applied": len(annotations),
        "output_size": output_path.stat().st_size
    }

def get_form_fields(input_path: Path) -> List[Dict[str, Any]]:
    """Extract interactive form fields from PDF."""
    doc = pymupdf.open(str(input_path))
    fields = []
    
    for p_idx, page in enumerate(doc):
        for widget in page.widgets():
            fields.append({
                "page": p_idx + 1,
                "name": widget.field_name,
                "type": widget.field_type_string,
                "value": widget.field_value or "",
                "rect": [widget.rect.x0, widget.rect.y0, widget.rect.x1, widget.rect.y1]
            })
    doc.close()
    return fields

def fill_pdf_forms(input_path: Path, output_path: Path, field_values: Dict[str, Any], flatten: bool = False) -> Dict[str, Any]:
    """Fill PDF AcroForm fields and optionally flatten."""
    doc = pymupdf.open(str(input_path))
    if doc.is_encrypted:
        doc.close()
        raise InvalidFileException("Document is encrypted.")
        
    filled_count = 0
    
    for page in doc:
        for widget in page.widgets():
            if widget.field_name in field_values:
                val = field_values[widget.field_name]
                widget.field_value = str(val) if val is not None else ""
                widget.update()
                filled_count += 1
                
    if flatten:
        # Flatten form fields into document content
        doc.bake()
        
    doc.save(str(output_path), garbage=4, deflate=True)
    doc.close()
    
    return {
        "fields_filled_count": filled_count,
        "flattened": flatten,
        "output_size": output_path.stat().st_size
    }


def resize_pdf(
    input_path: Path,
    output_path: Path,
    target_size: str = "A4",
    orientation: str = "portrait",
    fit_content: bool = True,
    margin: int = 18,
    pages: Optional[List[int]] = None
) -> Dict[str, Any]:
    """
    Resize PDF page dimensions to standard sizes (A4, A3, Letter, Legal, Tabloid),
    optionally scaling and centering existing content proportionally.
    """
    PAGE_DIMENSIONS = {
        "A4": (595.0, 842.0),
        "A3": (842.0, 1191.0),
        "A5": (420.0, 595.0),
        "Letter": (612.0, 792.0),
        "Legal": (612.0, 1008.0),
        "Tabloid": (792.0, 1224.0),
    }

    doc = pymupdf.open(str(input_path))
    if doc.is_encrypted:
        doc.close()
        raise InvalidFileException("Input PDF is encrypted.")
        
    total = len(doc)
    page_set = set(pages) if pages else set(range(1, total + 1))
    
    # Calculate target width & height
    base_w, base_h = PAGE_DIMENSIONS.get(target_size, (595.0, 842.0))
    if orientation == "landscape":
        target_w, target_h = max(base_w, base_h), min(base_w, base_h)
    else:
        target_w, target_h = min(base_w, base_h), max(base_w, base_h)
        
    out_doc = pymupdf.open()
    
    for i in range(total):
        orig_page = doc[i]
        orig_rect = orig_page.rect
        
        if (i + 1) not in page_set:
            # Keep original dimensions
            out_doc.insert_pdf(doc, from_page=i, to_page=i)
            continue
            
        new_page = out_doc.new_page(width=target_w, height=target_h)
        
        if fit_content:
            # Usable inner rect
            inner_w = target_w - (margin * 2)
            inner_h = target_h - (margin * 2)
            
            # Aspect ratio preservation
            orig_aspect = orig_rect.width / orig_rect.height
            target_aspect = inner_w / inner_h
            
            if orig_aspect > target_aspect:
                scaled_w = inner_w
                scaled_h = scaled_w / orig_aspect
            else:
                scaled_h = inner_h
                scaled_w = scaled_h * orig_aspect
                
            rx = (target_w - scaled_w) / 2
            ry = (target_h - scaled_h) / 2
            target_rect = pymupdf.Rect(rx, ry, rx + scaled_w, ry + scaled_h)
            new_page.show_pdf_page(target_rect, doc, i)
        else:
            # Direct placement from (margin, margin)
            target_rect = pymupdf.Rect(margin, margin, margin + orig_rect.width, margin + orig_rect.height)
            new_page.show_pdf_page(target_rect, doc, i)
            
    out_doc.save(str(output_path), garbage=4, deflate=True)
    out_doc.close()
    doc.close()
    
    return {
        "page_count": total,
        "target_size": target_size,
        "orientation": orientation,
        "width_pts": target_w,
        "height_pts": target_h,
        "output_size": output_path.stat().st_size
    }

def get_pdf_metadata(input_path: Path) -> Dict[str, Any]:
    """Retrieve PDF metadata and document properties."""
    doc = pymupdf.open(str(input_path))
    meta = doc.metadata or {}
    total = len(doc)
    
    dims = []
    if total > 0:
        first = doc[0].rect
        dims = [round(first.width, 1), round(first.height, 1)]
        
    doc.close()
    
    return {
        "title": meta.get("title") or "",
        "author": meta.get("author") or "",
        "subject": meta.get("subject") or "",
        "keywords": meta.get("keywords") or "",
        "creator": meta.get("creator") or "",
        "producer": meta.get("producer") or "",
        "creation_date": meta.get("creationDate") or "",
        "mod_date": meta.get("modDate") or "",
        "page_count": total,
        "first_page_dimensions": dims,
        "file_size": input_path.stat().st_size
    }

def update_pdf_metadata(input_path: Path, output_path: Path, metadata: Dict[str, str]) -> Dict[str, Any]:
    """Update PDF metadata fields cleanly."""
    doc = pymupdf.open(str(input_path))
    if doc.is_encrypted:
        doc.close()
        raise InvalidFileException("Input PDF is encrypted.")
        
    current = doc.metadata or {}
    updated = {
        "title": metadata.get("title", current.get("title", "")),
        "author": metadata.get("author", current.get("author", "")),
        "subject": metadata.get("subject", current.get("subject", "")),
        "keywords": metadata.get("keywords", current.get("keywords", "")),
        "creator": metadata.get("creator", current.get("creator", "PaperFlow")),
        "producer": metadata.get("producer", current.get("producer", "PaperFlow PDF Studio")),
    }
    
    doc.set_metadata(updated)
    doc.save(str(output_path), garbage=4, deflate=True)
    doc.close()
    
    return {
        "status": "Metadata Updated",
        "metadata": updated,
        "output_size": output_path.stat().st_size
    }

def extract_text_content(
    input_path: Path,
    output_path: Path,
    pages: Optional[List[int]] = None
) -> Dict[str, Any]:
    """Extract plain text from PDF and save as a UTF-8 text file."""
    doc = pymupdf.open(str(input_path))
    if doc.is_encrypted:
        doc.close()
        raise InvalidFileException("Input PDF is encrypted.")
        
    total = len(doc)
    page_set = set(pages) if pages else set(range(1, total + 1))
    
    extracted_pages = []
    full_text_parts = []
    
    for i in range(total):
        p_num = i + 1
        if p_num not in page_set:
            continue
        page = doc[i]
        txt = page.get_text().strip()
        extracted_pages.append({
            "page": p_num,
            "text": txt,
            "char_count": len(txt)
        })
        full_text_parts.append(f"--- Page {p_num} ---\n{txt}\n")
        
    doc.close()
    
    full_text = "\n".join(full_text_parts)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_text)
        
    total_chars = sum(p["char_count"] for p in extracted_pages)
    
    return {
        "status": "Extracted",
        "pages_extracted": len(extracted_pages),
        "total_characters": total_chars,
        "preview_text": full_text[:2000],
        "output_size": output_path.stat().st_size
    }

def flatten_pdf_forms(input_path: Path, output_path: Path) -> Dict[str, Any]:
    """Flatten/bake all interactive AcroForm fields and annotations into static PDF content."""
    doc = pymupdf.open(str(input_path))
    if doc.is_encrypted:
        doc.close()
        raise InvalidFileException("Input PDF is encrypted.")
        
    total = len(doc)
    # Bake forms and annotations into static appearance streams
    doc.bake()
    doc.save(str(output_path), garbage=4, deflate=True)
    doc.close()
    
    return {
        "status": "Flattened",
        "page_count": total,
        "output_size": output_path.stat().st_size,
        "message": "All form fields and annotations have been baked into permanent static content."
    }
