import pytest
import pymupdf
from pathlib import Path

from app.services.pdf.edit import resize_pdf, get_pdf_metadata, update_pdf_metadata, extract_text_content, flatten_pdf_forms
from app.services.pdf.optimize import remove_blank_pages, clean_and_deskew_pdf

@pytest.fixture
def sample_pdf(tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    doc = pymupdf.open()
    
    # Page 1: normal content
    p1 = doc.new_page(width=595, height=842)
    p1.insert_text((50, 80), "PaperFlow Document - Page 1", fontsize=16)
    p1.insert_text((50, 120), "This is real selectable text for extraction.", fontsize=12)
    
    # Page 2: completely blank page
    p2 = doc.new_page(width=595, height=842)
    
    # Page 3: content with signature line
    p3 = doc.new_page(width=595, height=842)
    p3.insert_text((50, 80), "Page 3 with text content", fontsize=14)
    p3.draw_rect(pymupdf.Rect(50, 200, 250, 250), color=(0, 0, 0), width=2)
    
    doc.save(str(pdf_path))
    doc.close()
    return pdf_path

def test_resize_pdf(tmp_path, sample_pdf):
    out_pdf = tmp_path / "resized.pdf"
    res = resize_pdf(sample_pdf, out_pdf, target_size="A3", orientation="landscape")
    assert out_pdf.exists()
    assert res["target_size"] == "A3"
    assert res["orientation"] == "landscape"
    
    doc = pymupdf.open(str(out_pdf))
    assert len(doc) == 3
    # A3 landscape: 1191 x 842 pt
    p = doc[0]
    assert round(p.rect.width) == 1191
    assert round(p.rect.height) == 842
    doc.close()

def test_pdf_metadata(tmp_path, sample_pdf):
    out_pdf = tmp_path / "meta_out.pdf"
    new_meta = {
        "title": "Quarterly Financial Analysis",
        "author": "Dr. Sarah Jenkins",
        "subject": "Corporate Audit 2026",
        "keywords": "finance, audit, pdf",
        "creator": "PaperFlow Studio"
    }
    update_res = update_pdf_metadata(sample_pdf, out_pdf, new_meta)
    assert out_pdf.exists()
    assert update_res["status"] == "Metadata Updated"
    
    read_meta = get_pdf_metadata(out_pdf)
    assert read_meta["title"] == "Quarterly Financial Analysis"
    assert read_meta["author"] == "Dr. Sarah Jenkins"
    assert read_meta["subject"] == "Corporate Audit 2026"
    assert read_meta["keywords"] == "finance, audit, pdf"

def test_extract_text_content(tmp_path, sample_pdf):
    out_txt = tmp_path / "extracted.txt"
    res = extract_text_content(sample_pdf, out_txt)
    assert out_txt.exists()
    assert res["status"] == "Extracted"
    assert "PaperFlow Document - Page 1" in res["preview_text"]
    assert "real selectable text" in res["preview_text"]

def test_remove_blank_pages(tmp_path, sample_pdf):
    out_pdf = tmp_path / "no_blanks.pdf"
    res = remove_blank_pages(sample_pdf, out_pdf)
    assert out_pdf.exists()
    assert res["original_page_count"] == 3
    assert res["removed_page_count"] == 1
    assert res["removed_pages"] == [2]
    assert res["resulting_page_count"] == 2
    
    doc = pymupdf.open(str(out_pdf))
    assert len(doc) == 2
    assert "Page 1" in doc[0].get_text()
    assert "Page 3" in doc[1].get_text()
    doc.close()

def test_clean_and_deskew_pdf(tmp_path, sample_pdf):
    out_pdf = tmp_path / "deskewed.pdf"
    res = clean_and_deskew_pdf(sample_pdf, out_pdf, deskew=True, enhance_contrast=True)
    assert out_pdf.exists()
    assert res["page_count"] == 3
    doc = pymupdf.open(str(out_pdf))
    assert len(doc) == 3
    doc.close()

def test_flatten_form(tmp_path, sample_pdf):
    out_pdf = tmp_path / "flattened.pdf"
    res = flatten_pdf_forms(sample_pdf, out_pdf)
    assert out_pdf.exists()
    assert res["status"] == "Flattened"
    doc = pymupdf.open(str(out_pdf))
    assert len(doc) == 3
    doc.close()
