import os
import re
import math
import collections
import zipfile
from pathlib import Path
from typing import Dict, Any, List, Optional
import pymupdf  # fitz
import pymupdf4llm
import httpx
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from app.core.config import settings
from app.core.errors import InvalidFileException, ProcessingException

def extract_pdf_text(input_path: Path) -> str:
    """Extract plain text from PDF."""
    doc = pymupdf.open(str(input_path))
    if doc.is_encrypted:
        doc.close()
        raise InvalidFileException("Document is encrypted.")
        
    full_text = []
    for page in doc:
        txt = page.get_text()
        if txt.strip():
            full_text.append(txt)
    doc.close()
    
    combined = "\n\n".join(full_text).strip()
    if not combined:
        raise ProcessingException("No text could be extracted from this PDF. If it is a scanned document, please run OCR first.")
    return combined

def _extractive_summarize(text: str, target_sentences: int = 5) -> Dict[str, Any]:
    """
    Extractive summarization algorithm using sentence scoring based on
    word frequency, position, and title heuristics.
    """
    raw_sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in raw_sentences if len(s.strip()) > 25 and not s.strip().startswith("http")]
    
    if len(sentences) <= target_sentences:
        return {
            "summary": " ".join(sentences),
            "key_points": sentences,
            "word_count": len(text.split()),
            "engine": "PaperFlow Intelligent Extractive Engine"
        }
        
    # Word frequency
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    stopwords = {
        'the', 'and', 'for', 'that', 'this', 'with', 'from', 'have', 'are', 'was', 'were',
        'will', 'would', 'there', 'their', 'they', 'about', 'which', 'when', 'what', 'some',
        'such', 'into', 'than', 'more', 'other', 'been', 'also', 'after', 'then', 'these'
    }
    filtered_words = [w for w in words if w not in stopwords]
    word_freq = collections.Counter(filtered_words)
    max_freq = max(word_freq.values()) if word_freq else 1
    
    # Score sentences
    scores = []
    for idx, s in enumerate(sentences):
        s_words = re.findall(r'\b[a-zA-Z]{3,}\b', s.lower())
        score = sum(word_freq.get(w, 0) / max_freq for w in s_words)
        # Position boost for start of document
        if idx < 3:
            score *= 1.3
        scores.append((score, idx, s))
        
    # Top sentences
    scores.sort(key=lambda x: x[0], reverse=True)
    top = sorted(scores[:target_sentences], key=lambda x: x[1])
    
    key_points = [item[2] for item in top]
    summary_paragraph = " ".join(key_points)
    
    return {
        "summary": summary_paragraph,
        "key_points": key_points,
        "word_count": len(text.split()),
        "engine": "PaperFlow Intelligent Extractive Engine"
    }

async def summarize_pdf(input_path: Path, length: str = "standard", focus: Optional[str] = None) -> Dict[str, Any]:
    """Generate structured summary from PDF text."""
    text = extract_pdf_text(input_path)
    
    num_points = 3 if length == "short" else (5 if length == "standard" else 8)
    
    # If OpenAI API Key is configured, use OpenAI
    if settings.OPENAI_API_KEY:
        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                prompt = f"Provide a structured summary of the following document. Include {num_points} key takeaway bullet points followed by a concise executive summary paragraph.\n\nDocument text:\n{text[:12000]}"
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
                    json={
                        "model": settings.OPENAI_MODEL,
                        "messages": [
                            {"role": "system", "content": "You are a professional document analyst."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.3
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    return {
                        "summary": content,
                        "key_points": [line.strip("- ") for line in content.splitlines() if line.strip().startswith("-")][:num_points],
                        "word_count": len(text.split()),
                        "engine": f"OpenAI ({settings.OPENAI_MODEL})"
                    }
        except Exception:
            pass
            
    # Intelligent extractive summarizer fallback
    result = _extractive_summarize(text, target_sentences=num_points)
    return result

async def translate_pdf(input_path: Path, output_path: Path, target_language: str = "Spanish") -> Dict[str, Any]:
    """Translate PDF text into target language and produce translated PDF document."""
    text = extract_pdf_text(input_path)
    
    translated_text = ""
    engine_used = ""
    
    if settings.OPENAI_API_KEY:
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                prompt = f"Translate the following text faithfully into {target_language}. Maintain formatting and paragraphs.\n\n{text[:10000]}"
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
                    json={
                        "model": settings.OPENAI_MODEL,
                        "messages": [
                            {"role": "system", "content": f"You are an expert translator specializing in technical and formal document translation to {target_language}."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.2
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    translated_text = data["choices"][0]["message"]["content"]
                    engine_used = f"OpenAI ({settings.OPENAI_MODEL})"
        except Exception:
            pass
            
    if not translated_text:
        # If no external API key, generate translated document structure with notice
        translated_text = (
            f"[Translation to {target_language}]\n\n"
            f"Original text length: {len(text.split())} words.\n\n"
            f"Notice: To perform live neural machine translation, configure an OPENAI_API_KEY in the PaperFlow environment settings.\n\n"
            f"Source text excerpt:\n{text[:3000]}"
        )
        engine_used = "Offline Document Parser"
        
    # Build translated PDF
    pdf_doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    styles = getSampleStyleSheet()
    story = [
        Paragraph(f"PaperFlow Translated Document ({target_language})", styles["Heading1"]),
        Spacer(1, 14)
    ]
    
    for para in translated_text.split("\n\n"):
        para = para.strip()
        if para:
            story.append(Paragraph(para.replace("\n", "<br/>"), styles["Normal"]))
            story.append(Spacer(1, 8))
            
    pdf_doc.build(story)
    
    return {
        "target_language": target_language,
        "engine": engine_used,
        "output_size": output_path.stat().st_size
    }

def pdf_to_markdown(input_path: Path, output_dir: Path) -> List[Path]:
    """
    Convert PDF to clean, structured Markdown using pymupdf4llm,
    preserving tables, headings, code, and extracting images.
    """
    if not input_path.exists():
        raise InvalidFileException("Input PDF not found.")
        
    base_name = input_path.stem
    image_dir = output_dir / f"{base_name}_images"
    image_dir.mkdir(parents=True, exist_ok=True)
    
    # Extract markdown with image extraction
    try:
        md_text = pymupdf4llm.to_markdown(
            str(input_path),
            write_images=True,
            image_path=str(image_dir)
        )
    except Exception as e:
        raise ProcessingException(f"Failed to convert PDF to Markdown: {str(e)}")
        
    md_file = output_dir / f"{base_name}.md"
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(md_text)
        
    created_files = [md_file]
    
    # Check if images were saved in image_dir
    images_found = list(image_dir.glob("*.*"))
    if images_found:
        zip_path = output_dir / f"{base_name}_markdown_with_assets.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
            z.write(md_file, arcname=md_file.name)
            for img in images_found:
                z.write(img, arcname=f"images/{img.name}")
        created_files.insert(0, zip_path)
        
    return created_files
