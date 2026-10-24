import os
import io
import pytest
import pymupdf  # fitz
from pathlib import Path
from PIL import Image

from app.services.pdf.organize import merge_pdfs, split_pdf, remove_pages, extract_pages, organize_pdf, scan_to_pdf
from app.services.pdf.optimize import compress_pdf, repair_pdf
from app.services.pdf.edit import rotate_pdf, add_page_numbers, add_watermark, crop_pdf, edit_pdf, fill_pdf_forms
from app.services.pdf.security import unlock_pdf, protect_pdf, sign_pdf, redact_pdf, compare_pdfs
from app.services.pdf.convert_from import pdf_to_images, pdf_to_docx, pdf_to_pptx, pdf_to_xlsx
from app.services.images.convert_to import images_to_pdf
from app.services.html.convert_to import html_to_pdf, sanitize_html
from app.services.intelligence.ai_service import summarize_pdf, pdf_to_markdown
from app.core.errors import InvalidFileException

@pytest.fixture
def temp_workspace(tmp_path):
    ws = tmp_path / "test_workspace"
    ws.mkdir()
    return ws

@pytest.fixture
def sample_pdf(temp_workspace):
    """Create a 3-page synthetic test PDF with text, rectangles, and fonts."""
    pdf_path = temp_workspace / "sample.pdf"
    doc = pymupdf.open()
    
    # Page 1
    p1 = doc.new_page(width=595, height=842)
    p1.insert_text((50, 72), "CONFIDENTIAL DOCUMENT - Page 1", fontsize=16)
    p1.insert_text((50, 120), "The secret code is SECRET-ALPHA-99.", fontsize=12)
    p1.draw_rect(pymupdf.Rect(50, 150, 300, 200), color=(0, 0, 1), fill=(0.9, 0.9, 1))
    
    # Page 2
    p2 = doc.new_page(width=595, height=842)
    p2.insert_text((50, 72), "Document Details - Page 2", fontsize=16)
    p2.insert_text((50, 120), "Second page with financial tables and numbers.", fontsize=12)
    
    # Page 3
    p3 = doc.new_page(width=595, height=842)
    p3.insert_text((50, 72), "Appendix - Page 3", fontsize=16)
    p3.insert_text((50, 120), "Final conclusions and notes.", fontsize=12)
    
    doc.save(str(pdf_path))
    doc.close()
    return pdf_path

def test_merge_pdfs(temp_workspace, sample_pdf):
    out_pdf = temp_workspace / "merged.pdf"
    res = merge_pdfs([sample_pdf, sample_pdf], out_pdf)
    assert out_pdf.exists()
    assert res["page_count"] == 6
    doc = pymupdf.open(str(out_pdf))
    assert len(doc) == 6
    doc.close()

def test_split_pdf_ranges(temp_workspace, sample_pdf):
    out_dir = temp_workspace / "split_out"
    out_dir.mkdir()
    files = split_pdf(sample_pdf, out_dir, mode="ranges", ranges="1,3")
    assert len(files) == 1
    doc = pymupdf.open(str(files[0]))
    assert len(doc) == 2
    doc.close()

def test_remove_pages(temp_workspace, sample_pdf):
    out_pdf = temp_workspace / "removed.pdf"
    res = remove_pages(sample_pdf, out_pdf, [2])
    assert res["resulting_page_count"] == 2
    doc = pymupdf.open(str(out_pdf))
    assert len(doc) == 2
    assert "Page 1" in doc[0].get_text()
    assert "Page 3" in doc[1].get_text()
    doc.close()

def test_remove_all_pages_fails(temp_workspace, sample_pdf):
    out_pdf = temp_workspace / "fail.pdf"
    with pytest.raises(InvalidFileException):
        remove_pages(sample_pdf, out_pdf, [1, 2, 3])

def test_organize_pdf(temp_workspace, sample_pdf):
    out_pdf = temp_workspace / "organized.pdf"
    actions = [
        {"page_num": 3, "rotation": 90, "duplicate_count": 1, "deleted": False},
        {"page_num": 1, "rotation": 0, "duplicate_count": 2, "deleted": False},
        {"page_num": 2, "deleted": True}
    ]
    res = organize_pdf(sample_pdf, out_pdf, actions)
    assert res["page_count"] == 3
    doc = pymupdf.open(str(out_pdf))
    assert len(doc) == 3
    assert doc[0].rotation == 90
    assert "Page 3" in doc[0].get_text()
    doc.close()

def test_compress_pdf_with_target(temp_workspace, sample_pdf):
    out_pdf = temp_workspace / "compressed.pdf"
    res = compress_pdf(sample_pdf, out_pdf, preset="recommended", custom_target_kb=50)
    assert out_pdf.exists()
    assert res["output_size"] > 0
    assert "target_achieved" in res
    assert "reduction_percentage" in res

def test_protect_and_unlock_pdf(temp_workspace, sample_pdf):
    prot_pdf = temp_workspace / "protected.pdf"
    unlock_pdf_path = temp_workspace / "unlocked.pdf"
    
    # Encrypt
    prot_res = protect_pdf(sample_pdf, prot_pdf, password="SecurePassword123")
    assert prot_pdf.exists()
    assert prot_res["status"] == "Protected"
    
    # Verify it is encrypted
    doc = pymupdf.open(str(prot_pdf))
    assert doc.is_encrypted
    doc.close()
    
    # Unlock with password
    unlock_res = unlock_pdf(prot_pdf, unlock_pdf_path, password="SecurePassword123")
    assert unlock_res["status"] == "Unlocked"
    unlocked_doc = pymupdf.open(str(unlock_pdf_path))
    assert not unlocked_doc.is_encrypted
    assert len(unlocked_doc) == 3
    unlocked_doc.close()

def test_redact_pdf_irreversible(temp_workspace, sample_pdf):
    out_pdf = temp_workspace / "redacted.pdf"
    res = redact_pdf(sample_pdf, out_pdf, redactions=[], search_terms=["SECRET-ALPHA-99"])
    assert out_pdf.exists()
    assert res["redactions_applied"] >= 1
    
    # Verify text is genuinely gone and CANNOT be extracted!
    doc = pymupdf.open(str(out_pdf))
    full_text = "".join(p.get_text() for p in doc)
    assert "SECRET-ALPHA-99" not in full_text
    doc.close()

def test_rotate_pdf(temp_workspace, sample_pdf):
    out_pdf = temp_workspace / "rotated.pdf"
    res = rotate_pdf(sample_pdf, out_pdf, angle=180, pages=[1])
    doc = pymupdf.open(str(out_pdf))
    assert doc[0].rotation == 180
    assert doc[1].rotation == 0
    doc.close()

def test_add_page_numbers(temp_workspace, sample_pdf):
    out_pdf = temp_workspace / "numbered.pdf"
    res = add_page_numbers(sample_pdf, out_pdf, position="bottom-center", format_str="Page {page} of {total}")
    doc = pymupdf.open(str(out_pdf))
    assert "Page 1 of 3" in doc[0].get_text()
    assert "Page 2 of 3" in doc[1].get_text()
    doc.close()

def test_compare_pdfs(temp_workspace, sample_pdf):
    # Create slightly modified copy
    mod_pdf = temp_workspace / "modified.pdf"
    doc = pymupdf.open(str(sample_pdf))
    p = doc.new_page(width=595, height=842)
    p.insert_text((50, 72), "Additional page 4 in modified version", fontsize=14)
    doc.save(str(mod_pdf))
    doc.close()
    
    out_dir = temp_workspace / "comp_out"
    out_dir.mkdir()
    res = compare_pdfs(sample_pdf, mod_pdf, out_dir)
    assert res["differences_found"] is True
    assert res["total_pages_compared"] == 4

def test_pdf_to_images(temp_workspace, sample_pdf):
    out_dir = temp_workspace / "img_out"
    out_dir.mkdir()
    files = pdf_to_images(sample_pdf, out_dir, format="png", dpi=100)
    assert len(files) >= 3  # pages + zip

def test_pdf_to_docx(temp_workspace, sample_pdf):
    out_docx = temp_workspace / "converted.docx"
    res = pdf_to_docx(sample_pdf, out_docx)
    assert out_docx.exists()
    assert res["status"] == "Converted"

def test_pdf_to_pptx(temp_workspace, sample_pdf):
    out_pptx = temp_workspace / "converted.pptx"
    res = pdf_to_pptx(sample_pdf, out_pptx)
    assert out_pptx.exists()
    assert res["slide_count"] == 3

def test_html_to_pdf_ssrf_blocking(temp_workspace):
    out_pdf = temp_workspace / "html_test.pdf"
    
    # Safe HTML
    safe_html = "<h1>Safe Title</h1><p>This is safe document content.</p>"
    res = html_to_pdf(safe_html, out_pdf)
    assert out_pdf.exists()
    assert res["status"] == "Rendered"
    
    # Blocked SSRF attempts
    with pytest.raises(InvalidFileException):
        html_to_pdf('<img src="http://169.254.169.254/latest/meta-data/" />', out_pdf)
        
    with pytest.raises(InvalidFileException):
        html_to_pdf('<iframe src="file:///etc/passwd"></iframe>', out_pdf)

def test_pdf_to_markdown(temp_workspace, sample_pdf):
    out_dir = temp_workspace / "md_out"
    out_dir.mkdir()
    files = pdf_to_markdown(sample_pdf, out_dir)
    assert len(files) >= 1
    assert any(f.suffix == ".md" for f in files)
