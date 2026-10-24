import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any
import docx
import openpyxl
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from app.core.config import settings
from app.core.errors import InvalidFileException, ProcessingException

def _try_libreoffice_conversion(input_path: Path, output_path: Path) -> bool:
    """Attempt conversion using headless LibreOffice if installed."""
    soffice_cmd = settings.LIBREOFFICE_PATH or shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice_cmd:
        return False
        
    try:
        out_dir = output_path.parent
        cmd = [
            soffice_cmd,
            "--headless",
            "--convert-to", "pdf",
            "--outdir", str(out_dir),
            str(input_path)
        ]
        res = subprocess.run(cmd, capture_output=True, timeout=60)
        expected_pdf = out_dir / f"{input_path.stem}.pdf"
        if expected_pdf.exists() and expected_pdf.stat().st_size > 0:
            if expected_pdf != output_path:
                shutil.move(str(expected_pdf), str(output_path))
            return True
    except Exception:
        pass
    return False

def docx_to_pdf(input_path: Path, output_path: Path) -> Dict[str, Any]:
    """Convert DOCX file to PDF."""
    if _try_libreoffice_conversion(input_path, output_path):
        return {
            "engine": "LibreOffice",
            "output_size": output_path.stat().st_size
        }
        
    # Python-based high fidelity document converter
    try:
        doc = docx.Document(str(input_path))
        pdf_doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            rightMargin=54,
            leftMargin=54,
            topMargin=54,
            bottomMargin=54
        )
        
        styles = getSampleStyleSheet()
        normal_style = styles["Normal"]
        h1_style = styles["Heading1"]
        h2_style = styles["Heading2"]
        
        story = []
        
        for p in doc.paragraphs:
            txt = p.text.strip()
            if not txt:
                story.append(Spacer(1, 8))
                continue
            if p.style.name.startswith("Heading 1"):
                story.append(Paragraph(txt, h1_style))
                story.append(Spacer(1, 10))
            elif p.style.name.startswith("Heading 2"):
                story.append(Paragraph(txt, h2_style))
                story.append(Spacer(1, 8))
            else:
                story.append(Paragraph(txt, normal_style))
                story.append(Spacer(1, 6))
                
        # Also process tables
        for tbl in doc.tables:
            tbl_data = []
            for row in tbl.rows:
                tbl_data.append([cell.text.strip() for cell in row.cells])
            if tbl_data:
                t = Table(tbl_data)
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#334155")),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ]))
                story.append(t)
                story.append(Spacer(1, 12))
                
        if not story:
            story.append(Paragraph("Empty Document", normal_style))
            
        pdf_doc.build(story)
        
        return {
            "engine": "Python Document Converter",
            "output_size": output_path.stat().st_size
        }
    except Exception as e:
        raise ProcessingException(f"DOCX to PDF conversion failed: {str(e)}")

def xlsx_to_pdf(input_path: Path, output_path: Path) -> Dict[str, Any]:
    """Convert Excel XLSX spreadsheet to PDF."""
    if _try_libreoffice_conversion(input_path, output_path):
        return {
            "engine": "LibreOffice",
            "output_size": output_path.stat().st_size
        }
        
    try:
        wb = openpyxl.load_workbook(str(input_path), data_only=True)
        pdf_doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )
        
        styles = getSampleStyleSheet()
        h2_style = styles["Heading2"]
        story = []
        
        for sheetname in wb.sheetnames:
            ws = wb[sheetname]
            story.append(Paragraph(f"Worksheet: {sheetname}", h2_style))
            story.append(Spacer(1, 8))
            
            data = []
            for row in ws.iter_rows(values_only=True):
                # Only include non-empty rows
                if any(cell is not None for cell in row):
                    data.append([str(c) if c is not None else "" for c in row])
                    
            if data:
                # Cap max columns to prevent table overflow
                max_cols = 8
                sliced_data = [r[:max_cols] for r in data[:100]]
                t = Table(sliced_data)
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E293B")),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#94A3B8")),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ]))
                story.append(t)
            story.append(Spacer(1, 16))
            
        if not story:
            story.append(Paragraph("Empty Spreadsheet", styles["Normal"]))
            
        pdf_doc.build(story)
        
        return {
            "engine": "Python Spreadsheet Converter",
            "output_size": output_path.stat().st_size
        }
    except Exception as e:
        raise ProcessingException(f"Excel to PDF conversion failed: {str(e)}")

def pptx_to_pdf(input_path: Path, output_path: Path) -> Dict[str, Any]:
    """Convert PowerPoint PPTX presentation to PDF."""
    if _try_libreoffice_conversion(input_path, output_path):
        return {
            "engine": "LibreOffice",
            "output_size": output_path.stat().st_size
        }
        
    try:
        import pptx
        prs = pptx.Presentation(str(input_path))
        pdf_doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )
        
        styles = getSampleStyleSheet()
        h1_style = styles["Heading1"]
        normal_style = styles["Normal"]
        story = []
        
        for idx, slide in enumerate(prs.slides):
            story.append(Paragraph(f"Slide {idx + 1}", h1_style))
            story.append(Spacer(1, 10))
            
            for shape in slide.shapes:
                if shape.has_text_frame:
                    for para in shape.text_frame.paragraphs:
                        txt = para.text.strip()
                        if txt:
                            story.append(Paragraph(txt, normal_style))
                            story.append(Spacer(1, 4))
            story.append(Spacer(1, 20))
            
        if not story:
            story.append(Paragraph("Empty Presentation", normal_style))
            
        pdf_doc.build(story)
        
        return {
            "engine": "Python Presentation Converter",
            "output_size": output_path.stat().st_size
        }
    except Exception as e:
        raise ProcessingException(f"PowerPoint to PDF conversion failed: {str(e)}")
