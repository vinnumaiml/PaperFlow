import re
import html
from pathlib import Path
from typing import Dict, Any
from reportlab.lib.pagesizes import A4, letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from app.core.errors import InvalidFileException, ProcessingException

# Regex patterns to sanitize HTML and protect against SSRF/LFI
UNSAFE_TAGS_RE = re.compile(r'<(script|iframe|object|embed|link|meta|base|form)[^>]*>.*?</\1>', re.IGNORECASE | re.DOTALL)
UNSAFE_SELF_CLOSING_RE = re.compile(r'<(script|iframe|object|embed|link|meta|base|form)[^>]*/>', re.IGNORECASE)
UNSAFE_ATTRS_RE = re.compile(r'\b(on\w+|formaction)\s*=\s*["\'][^"\']*["\']', re.IGNORECASE)
FILE_PROTO_RE = re.compile(r'\b(file|gopher|dict|data):', re.IGNORECASE)
SSRF_URL_RE = re.compile(r'https?://(localhost|127\.\d+\.\d+\.\d+|10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+|172\.(1[6-9]|2\d|3[01])\.\d+\.\d+|169\.254\.\d+\.\d+|0\.0\.0\.0|\[::1\])', re.IGNORECASE)

def sanitize_html(raw_html: str) -> str:
    """Strip malicious tags, local file references, and internal network endpoints."""
    # Check for SSRF attempts
    if FILE_PROTO_RE.search(raw_html):
        raise InvalidFileException("Prohibited protocol detected: arbitrary local file access is blocked.")
    if SSRF_URL_RE.search(raw_html):
        raise InvalidFileException("Prohibited network endpoint: internal host access is blocked.")
        
    cleaned = UNSAFE_TAGS_RE.sub('', raw_html)
    cleaned = UNSAFE_SELF_CLOSING_RE.sub('', cleaned)
    cleaned = UNSAFE_ATTRS_RE.sub('', cleaned)
    return cleaned

def html_to_pdf(html_content: str, output_path: Path, page_size: str = "A4", margin_mm: int = 15) -> Dict[str, Any]:
    """Render sanitized HTML content to PDF."""
    if not html_content.strip():
        raise InvalidFileException("HTML content is empty.")
        
    safe_html = sanitize_html(html_content)
    
    # Strip basic HTML tags into formatted paragraphs
    pdf_doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4 if page_size == "A4" else letter,
        rightMargin=margin_mm * 2.83,
        leftMargin=margin_mm * 2.83,
        topMargin=margin_mm * 2.83,
        bottomMargin=margin_mm * 2.83
    )
    
    styles = getSampleStyleSheet()
    normal = styles["Normal"]
    h1 = styles["Heading1"]
    h2 = styles["Heading2"]
    
    story = []
    
    # Extract headers and paragraphs using simple regex
    body_match = re.search(r'<body[^>]*>(.*?)</body>', safe_html, re.DOTALL | re.IGNORECASE)
    body_content = body_match.group(1) if body_match else safe_html
    
    # Simple tag tokenizer for clean ReportLab paragraphs
    lines = re.split(r'<(?:p|h1|h2|h3|div|br)[^>]*>', body_content, flags=re.IGNORECASE)
    
    for line in lines:
        cleaned_line = re.sub(r'<[^>]+>', '', line).strip()
        cleaned_line = html.unescape(cleaned_line)
        if cleaned_line:
            if len(cleaned_line) < 60 and ("<h1" in line.lower() or cleaned_line.isupper()):
                story.append(Paragraph(cleaned_line, h1))
                story.append(Spacer(1, 10))
            else:
                story.append(Paragraph(cleaned_line, normal))
                story.append(Spacer(1, 6))
                
    if not story:
        story.append(Paragraph("Document generated from HTML", normal))
        
    pdf_doc.build(story)
    
    return {
        "status": "Rendered",
        "page_size": page_size,
        "output_size": output_path.stat().st_size
    }
