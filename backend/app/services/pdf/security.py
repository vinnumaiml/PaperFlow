import os
import io
import base64
import difflib
import zipfile
from pathlib import Path
from typing import List, Dict, Any, Optional
import pymupdf  # fitz
import pikepdf
from PIL import Image, ImageChops

from app.core.errors import InvalidFileException, ProcessingException

def unlock_pdf(input_path: Path, output_path: Path, password: str) -> Dict[str, Any]:
    """Decrypt a password-protected PDF using user credentials."""
    try:
        with pikepdf.open(str(input_path), password=password) as doc:
            doc.save(str(output_path))
    except pikepdf.PasswordError:
        raise InvalidFileException("Incorrect password provided for encrypted document.")
    except Exception as e:
        raise ProcessingException(f"Failed to decrypt document: {str(e)}")
        
    # Verify unlocked file
    try:
        doc_ver = pymupdf.open(str(output_path))
        if doc_ver.is_encrypted:
            doc_ver.close()
            raise ProcessingException("Failed to fully decrypt file.")
        page_count = len(doc_ver)
        doc_ver.close()
    except Exception as e:
        raise ProcessingException(f"Decryption verification failed: {str(e)}")
        
    return {
        "status": "Unlocked",
        "page_count": page_count,
        "output_size": output_path.stat().st_size
    }

def protect_pdf(input_path: Path, output_path: Path, password: str, allow_printing: bool = True, allow_copying: bool = True) -> Dict[str, Any]:
    """Encrypt a PDF with user password and permissions."""
    if not password:
        raise InvalidFileException("Password cannot be empty.")
        
    try:
        permissions = pikepdf.Permissions(
            extract=allow_copying,
            print_lowres=allow_printing,
            print_highres=allow_printing
        )
        
        with pikepdf.open(str(input_path)) as doc:
            enc = pikepdf.Encryption(
                owner=password,
                user=password,
                R=6,  # 256-bit AES
                allow=permissions
            )
            doc.save(str(output_path), encryption=enc)
    except Exception as e:
        raise ProcessingException(f"Failed to encrypt document: {str(e)}")
        
    # Validate output by testing decryption with password
    try:
        with pikepdf.open(str(output_path), password=password) as check_doc:
            pass
    except Exception:
        raise ProcessingException("Verification of encrypted document failed.")
        
    return {
        "status": "Protected",
        "encryption": "AES-256",
        "output_size": output_path.stat().st_size
    }

def sign_pdf(input_path: Path, output_path: Path, signatures: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Embed visual signatures (drawn/typed/uploaded) onto specified PDF pages."""
    doc = pymupdf.open(str(input_path))
    if doc.is_encrypted:
        doc.close()
        raise InvalidFileException("Document is encrypted.")
        
    total = len(doc)
    temp_imgs: List[Path] = []
    
    try:
        for idx, sig in enumerate(signatures):
            p_num = sig.get("page", 1)
            if p_num < 1 or p_num > total:
                continue
                
            page = doc[p_num - 1]
            data_url = sig.get("image_data", "")
            
            if "," in data_url:
                header, encoded = data_url.split(",", 1)
            else:
                encoded = data_url
                
            img_bytes = base64.b64decode(encoded)
            
            # Temporary signature image file
            sig_file = output_path.parent / f"sig_temp_{idx}.png"
            with open(sig_file, "wb") as f:
                f.write(img_bytes)
            temp_imgs.append(sig_file)
            
            x = float(sig.get("x", 100))
            y = float(sig.get("y", 100))
            w = float(sig.get("width", 150))
            h = float(sig.get("height", 60))
            
            rect = pymupdf.Rect(x, y, x + w, y + h)
            page.insert_image(rect, filename=str(sig_file), overlay=True)
            
        doc.save(str(output_path), garbage=4, deflate=True)
        doc.close()
    finally:
        for f in temp_imgs:
            if f.exists():
                f.unlink(missing_ok=True)
                
    return {
        "signatures_applied": len(signatures),
        "output_size": output_path.stat().st_size
    }

def redact_pdf(input_path: Path, output_path: Path, redactions: List[Dict[str, Any]], search_terms: List[str]) -> Dict[str, Any]:
    """
    Perform real irreversible redaction:
    Removes underlying text, images, and vector content.
    """
    doc = pymupdf.open(str(input_path))
    if doc.is_encrypted:
        doc.close()
        raise InvalidFileException("Document is encrypted.")
        
    total = len(doc)
    redaction_count = 0
    
    # Process text search terms
    for term in search_terms:
        term = term.strip()
        if not term:
            continue
        for page in doc:
            quads = page.search_for(term)
            for quad in quads:
                page.add_redact_annot(quad, fill=(0, 0, 0))
                redaction_count += 1
                
    # Process coordinate-based redactions
    for item in redactions:
        p_num = item.get("page", 1)
        if p_num < 1 or p_num > total:
            continue
        page = doc[p_num - 1]
        
        x = float(item.get("x", 0))
        y = float(item.get("y", 0))
        w = float(item.get("width", 100))
        h = float(item.get("height", 30))
        rect = pymupdf.Rect(x, y, x + w, y + h)
        page.add_redact_annot(rect, fill=(0, 0, 0))
        redaction_count += 1
        
    # Irreversibly apply redactions
    for page in doc:
        page.apply_redactions()
        
    doc.save(str(output_path), garbage=4, deflate=True, clean=True)
    doc.close()
    
    # Test that redaction was irreversible by checking exported text
    doc_ver = pymupdf.open(str(output_path))
    for term in search_terms:
        if term:
            for page in doc_ver:
                found = page.search_for(term)
                if len(found) > 0:
                    doc_ver.close()
                    raise ProcessingException(f"Redaction failed: term '{term}' was still extractable from file.")
    doc_ver.close()
    
    return {
        "redactions_applied": redaction_count,
        "output_size": output_path.stat().st_size
    }

def compare_pdfs(pdf1_path: Path, pdf2_path: Path, output_dir: Path) -> Dict[str, Any]:
    """
    Compare two PDF files:
    - Text diff page by page
    - Structural differences
    - Visual difference rendering (pixel diff overlay)
    """
    doc1 = pymupdf.open(str(pdf1_path))
    doc2 = pymupdf.open(str(pdf2_path))
    
    pages1 = len(doc1)
    pages2 = len(doc2)
    max_pages = max(pages1, pages2)
    
    page_comparisons = []
    visual_diff_images: List[Path] = []
    
    for i in range(max_pages):
        text1 = doc1[i].get_text() if i < pages1 else "[Page does not exist in File 1]"
        text2 = doc2[i].get_text() if i < pages2 else "[Page does not exist in File 2]"
        
        # Calculate diff lines
        diff = list(difflib.unified_diff(
            text1.splitlines(keepends=True),
            text2.splitlines(keepends=True),
            fromfile=f"File 1 Page {i+1}",
            tofile=f"File 2 Page {i+1}"
        ))
        
        diff_text = "".join(diff)
        has_text_diff = len(diff) > 0
        
        # Render visual difference image if both pages exist
        visual_path = None
        has_visual_diff = False
        
        if i < pages1 and i < pages2:
            pix1 = doc1[i].get_pixmap(dpi=100)
            pix2 = doc2[i].get_pixmap(dpi=100)
            
            img1 = Image.open(io.BytesIO(pix1.tobytes("png")))
            img2 = Image.open(io.BytesIO(pix2.tobytes("png")))
            
            # Resize to match if dimensions differ
            if img1.size != img2.size:
                img2 = img2.resize(img1.size)
                
            diff_img = ImageChops.difference(img1.convert("RGB"), img2.convert("RGB"))
            
            # Check bounding box of differences
            bbox = diff_img.getbbox()
            if bbox is not None:
                has_visual_diff = True
                # Highlight differences in red overlay
                diff_file = output_dir / f"visual_diff_page_{i + 1}.png"
                diff_img.save(str(diff_file))
                visual_diff_images.append(diff_file)
                visual_path = diff_file.name
                
        page_comparisons.append({
            "page": i + 1,
            "has_text_diff": has_text_diff,
            "has_visual_diff": has_visual_diff,
            "diff_snippet": diff_text[:1000] if diff_text else "No textual differences.",
            "visual_image": visual_path
        })
        
    doc1.close()
    doc2.close()
    
    # Save a comparison summary report
    report_file = output_dir / "comparison_report.txt"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("=== PaperFlow PDF Comparison Report ===\n\n")
        f.write(f"File 1: {pdf1_path.name} ({pages1} pages)\n")
        f.write(f"File 2: {pdf2_path.name} ({pages2} pages)\n\n")
        for pc in page_comparisons:
            f.write(f"--- Page {pc['page']} ---\n")
            f.write(f"Text differences: {'YES' if pc['has_text_diff'] else 'None'}\n")
            f.write(f"Visual differences: {'YES' if pc['has_visual_diff'] else 'None'}\n")
            if pc['has_text_diff']:
                f.write(pc['diff_snippet'] + "\n\n")
                
    # Also package visual diff images and report in a ZIP
    zip_path = output_dir / "comparison_package.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(report_file, arcname=report_file.name)
        for img in visual_diff_images:
            z.write(img, arcname=img.name)
            
    return {
        "file1_pages": pages1,
        "file2_pages": pages2,
        "total_pages_compared": max_pages,
        "differences_found": any(p["has_text_diff"] or p["has_visual_diff"] for p in page_comparisons),
        "page_details": page_comparisons,
        "report_file": report_file.name,
        "zip_file": zip_path.name
    }
