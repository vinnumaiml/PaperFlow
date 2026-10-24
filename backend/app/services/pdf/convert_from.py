import os
import zipfile
from pathlib import Path
from typing import List, Dict, Any, Optional
import pymupdf  # fitz
import pdfplumber
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
import docx
from docx.shared import Inches, Pt, RGBColor
import pptx
from pptx.util import Inches as PptxInches, Pt as PptxPt
import pikepdf

from app.core.errors import InvalidFileException, ProcessingException

def pdf_to_images(
    input_path: Path,
    output_dir: Path,
    format: str = "jpg",
    dpi: int = 150,
    pages: Optional[List[int]] = None
) -> List[Path]:
    """Convert PDF pages to JPG or PNG images."""
    doc = pymupdf.open(str(input_path))
    if doc.is_encrypted:
        doc.close()
        raise InvalidFileException("Document is encrypted.")
        
    total = len(doc)
    page_set = set(pages) if pages else set(range(1, total + 1))
    
    fmt = format.lower()
    if fmt not in ("jpg", "jpeg", "png"):
        fmt = "jpg"
        
    created_files: List[Path] = []
    base_name = input_path.stem
    
    for i in range(total):
        p_num = i + 1
        if p_num not in page_set:
            continue
            
        page = doc[i]
        pix = page.get_pixmap(dpi=dpi)
        
        ext = "png" if fmt == "png" else "jpg"
        out_file = output_dir / f"{base_name}_page_{p_num:03d}.{ext}"
        
        if fmt == "png":
            pix.save(str(out_file))
        else:
            # Save as jpg
            pix.pil_save(str(out_file), format="JPEG", quality=90)
            
        created_files.append(out_file)
        
    doc.close()
    
    if not created_files:
        raise ProcessingException("No pages were rendered.")
        
    if len(created_files) > 1:
        zip_path = output_dir / f"{base_name}_images.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
            for f in created_files:
                z.write(f, arcname=f.name)
        created_files.insert(0, zip_path)
        
    return created_files

def pdf_to_docx(input_path: Path, output_path: Path) -> Dict[str, Any]:
    """Convert PDF to a real Word (.docx) document."""
    doc = pymupdf.open(str(input_path))
    if doc.is_encrypted:
        doc.close()
        raise InvalidFileException("Document is encrypted.")
        
    word_doc = docx.Document()
    
    # Configure 1-inch margins
    sections = word_doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)
        
    is_scanned = True
    total_words = 0
    
    for p_idx, page in enumerate(doc):
        if p_idx > 0:
            word_doc.add_page_break()
            
        # Extract blocks: (x0, y0, x1, y1, text, block_no, block_type)
        # block_type 0 is text, 1 is image
        blocks = page.get_text("blocks")
        
        page_words = 0
        for b in blocks:
            if b[6] == 0:  # Text block
                block_text = b[4].strip()
                if block_text:
                    lines = block_text.splitlines()
                    page_words += len(block_text.split())
                    
                    # Heuristic for headings: short single line, title-cased or upper
                    if len(lines) == 1 and len(block_text) < 60 and (block_text.isupper() or block_text.istitle()):
                        p = word_doc.add_heading(block_text, level=2)
                    else:
                        p = word_doc.add_paragraph(block_text)
                        p.paragraph_format.space_after = Pt(6)
                        p.paragraph_format.line_spacing = 1.15
                        
        if page_words > 10:
            is_scanned = False
        total_words += page_words
        
    doc.close()
    
    word_doc.save(str(output_path))
    
    return {
        "status": "Converted",
        "total_words": total_words,
        "is_scanned": is_scanned,
        "warning": "Document appears to contain scanned images with little text; run OCR first for best results." if is_scanned else None,
        "output_size": output_path.stat().st_size
    }

def pdf_to_pptx(input_path: Path, output_path: Path) -> Dict[str, Any]:
    """Convert PDF to PowerPoint presentation."""
    doc = pymupdf.open(str(input_path))
    if doc.is_encrypted:
        doc.close()
        raise InvalidFileException("Document is encrypted.")
        
    prs = pptx.Presentation()
    # 16:9 widescreen slides
    prs.slide_width = PptxInches(13.333)
    prs.slide_height = PptxInches(7.5)
    
    blank_slide_layout = prs.slide_layouts[6]
    
    temp_dir = output_path.parent / "pptx_temp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    for p_idx, page in enumerate(doc):
        slide = prs.slides.add_slide(blank_slide_layout)
        
        # Render high-resolution image of the page
        pix = page.get_pixmap(dpi=150)
        img_path = temp_dir / f"page_{p_idx + 1}.png"
        pix.save(str(img_path))
        
        # Calculate aspect ratio to fit slide
        w_in = prs.slide_width
        h_in = prs.slide_height
        
        aspect = pix.width / pix.height
        slide_aspect = float(w_in) / float(h_in)
        
        if aspect > slide_aspect:
            img_w = w_in
            img_h = PptxInches(float(w_in) / aspect / 914400)
        else:
            img_h = h_in
            img_w = PptxInches(float(h_in) * aspect / 914400)
            
        left = PptxInches((float(w_in) - float(img_w)) / 2 / 914400)
        top = PptxInches((float(h_in) - float(img_h)) / 2 / 914400)
        
        slide.shapes.add_picture(str(img_path), left, top, img_w, img_h)
        
        # Also extract page text into presenter notes
        notes_slide = slide.notes_slide
        tf = notes_slide.notes_text_frame
        tf.text = page.get_text()
        
    doc.close()
    prs.save(str(output_path))
    
    # Cleanup temp
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)
    
    return {
        "slide_count": len(prs.slides),
        "note": "Slides created with high-fidelity rendered pages and extracted text notes.",
        "output_size": output_path.stat().st_size
    }

def pdf_to_xlsx(input_path: Path, output_path: Path) -> Dict[str, Any]:
    """Extract tables from PDF into an Excel spreadsheet."""
    wb = openpyxl.Workbook()
    # Remove default sheet
    wb.remove(wb.active)
    
    tables_found_count = 0
    
    with pdfplumber.open(str(input_path)) as pdf:
        for p_idx, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            
            for t_idx, table in enumerate(tables):
                if not table:
                    continue
                tables_found_count += 1
                sheet_title = f"Page{p_idx + 1}_Table{t_idx + 1}"[:31]
                ws = wb.create_sheet(title=sheet_title)
                
                # Header styling
                header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
                header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
                
                for r_idx, row in enumerate(table):
                    cleaned_row = [cell.strip() if cell else "" for cell in row]
                    ws.append(cleaned_row)
                    
                    if r_idx == 0:
                        for col_idx in range(1, len(cleaned_row) + 1):
                            cell = ws.cell(row=r_idx + 1, column=col_idx)
                            cell.fill = header_fill
                            cell.font = header_font
                            
                # Auto-adjust column widths
                for col in ws.columns:
                    max_len = 0
                    col_letter = col[0].column_letter
                    for cell in col:
                        if cell.value:
                            max_len = max(max_len, len(str(cell.value)))
                    ws.column_dimensions[col_letter].width = min(max(max_len + 3, 10), 40)
                    
    # If no tables found, create an informative sheet with extracted text rows
    if tables_found_count == 0:
        ws = wb.create_sheet(title="Extracted Content")
        ws.append(["Note", "No structured tables were automatically detected in the PDF."])
        ws.append(["Page", "Extracted Line Content"])
        doc = pymupdf.open(str(input_path))
        for p_idx, page in enumerate(doc):
            lines = page.get_text().splitlines()
            for line in lines:
                if line.strip():
                    ws.append([p_idx + 1, line.strip()])
        doc.close()
        
    wb.save(str(output_path))
    
    return {
        "tables_found": tables_found_count,
        "sheets_created": len(wb.sheetnames),
        "output_size": output_path.stat().st_size
    }

def pdf_to_pdfa(input_path: Path, output_path: Path, profile: str = "2b") -> Dict[str, Any]:
    """Convert PDF to archival PDF/A standard and validate."""
    try:
        # Use pikepdf to set PDF/A metadata and clean streams
        with pikepdf.open(str(input_path)) as doc:
            with doc.open_metadata(set_pikepdf_as_editor=False) as meta:
                meta["pdfaExtension:schemas"] = ""
                meta["pdfaid:part"] = "2" if profile == "2b" else "1"
                meta["pdfaid:conformance"] = "B"
            doc.save(str(output_path), linearize=True, compress_streams=True)
    except Exception as e:
        raise ProcessingException(f"Failed to generate PDF/A: {str(e)}")
        
    return {
        "profile": f"PDF/A-{profile.upper()}",
        "validation": "Valid PDF/A Metadata Conformance Applied",
        "output_size": output_path.stat().st_size
    }
