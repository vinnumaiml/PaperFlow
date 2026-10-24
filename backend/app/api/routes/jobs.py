import json
import mimetypes
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Query
from fastapi.responses import FileResponse

from app.core.config import settings
from app.core.errors import InvalidFileException, JobNotFoundException, ProcessingException
from app.schemas.job import JobResponse, JobStatus, OutputFile
from app.services.storage import storage_service
from app.services.jobs_manager import jobs_manager

# PDF Services
from app.services.pdf.organize import merge_pdfs, split_pdf, remove_pages, extract_pages, organize_pdf, scan_to_pdf
from app.services.pdf.optimize import compress_pdf, repair_pdf, remove_blank_pages, clean_and_deskew_pdf
from app.services.pdf.edit import (
    rotate_pdf,
    add_page_numbers,
    add_watermark,
    crop_pdf,
    edit_pdf,
    fill_pdf_forms,
    resize_pdf,
    get_pdf_metadata,
    update_pdf_metadata,
    extract_text_content,
    flatten_pdf_forms,
)
from app.services.pdf.security import unlock_pdf, protect_pdf, sign_pdf, redact_pdf, compare_pdfs
from app.services.pdf.convert_from import pdf_to_images, pdf_to_docx, pdf_to_pptx, pdf_to_xlsx, pdf_to_pdfa
from app.services.images.convert_to import images_to_pdf
from app.services.office.convert_to import docx_to_pdf, pptx_to_pdf, xlsx_to_pdf
from app.services.html.convert_to import html_to_pdf
from app.services.ocr.ocr_service import ocr_pdf
from app.services.intelligence.ai_service import summarize_pdf, translate_pdf, pdf_to_markdown

router = APIRouter()

@router.post("/jobs", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    tool: str = Form(...),
    options: Optional[str] = Form(None),
    files: List[UploadFile] = File(default_factory=list),
    html_content: Optional[str] = Form(None)
):
    """
    Upload files, validate the tool and options, and launch document processing.
    """
    parsed_options = {}
    if options:
        try:
            parsed_options = json.loads(options)
        except Exception:
            raise InvalidFileException("Options must be valid JSON.")
            
    # Check batch limit
    if len(files) > settings.MAX_BATCH_FILES:
        raise InvalidFileException(f"Cannot upload more than {settings.MAX_BATCH_FILES} files in one batch.")
        
    job_id = jobs_manager.create_job(tool=tool, file_count=len(files) if files else 1)
    
    # Save uploaded files into the isolated job workspace
    saved_input_paths: List[Path] = []
    for f in files:
        content = await f.read()
        saved_path = storage_service.save_upload_file(job_id, f.filename or "uploaded_file", content)
        saved_input_paths.append(saved_path)
        
    workspace = storage_service.get_job_dir(job_id)
    outputs_dir = workspace / "outputs"
    
    # Define async execution pipeline for the requested tool
    async def process_task():
        task_input_paths = list(saved_input_paths)
        jobs_manager.update_progress(job_id, "Validating", 20, "Validating input files")
        output_files: List[OutputFile] = []
        stats: dict = {}
        
        try:
            # 1. Organize PDF
            if tool == "merge-pdf":
                if len(task_input_paths) < 2:
                    raise InvalidFileException("At least two PDF files are required for merging.")
                # Respect custom file order if supplied
                file_order = parsed_options.get("file_order")
                if file_order:
                    ordered_paths = []
                    name_map = {p.name: p for p in task_input_paths}
                    for name in file_order:
                        if name in name_map:
                            ordered_paths.append(name_map[name])
                    if len(ordered_paths) == len(task_input_paths):
                        task_input_paths = ordered_paths
                        
                out_path = outputs_dir / "merged_document.pdf"
                jobs_manager.update_progress(job_id, "Merging", 50, "Merging PDF pages in order...")
                stats = merge_pdfs(task_input_paths, out_path)
                output_files.append(OutputFile(
                    filename=out_path.name,
                    size_bytes=out_path.stat().st_size,
                    download_url=f"/api/jobs/{job_id}/download?filename={out_path.name}",
                    mime_type="application/pdf"
                ))
                
            elif tool == "split-pdf":
                if not task_input_paths:
                    raise InvalidFileException("No PDF file uploaded.")
                mode = parsed_options.get("mode", "ranges")
                ranges = parsed_options.get("ranges", "1")
                group_size = int(parsed_options.get("group_size", 1))
                jobs_manager.update_progress(job_id, "Splitting", 50, f"Splitting PDF ({mode})...")
                created = split_pdf(task_input_paths[0], outputs_dir, mode=mode, ranges=ranges, group_size=group_size)
                for f in created:
                    mime = "application/zip" if f.suffix == ".zip" else "application/pdf"
                    output_files.append(OutputFile(
                        filename=f.name,
                        size_bytes=f.stat().st_size,
                        download_url=f"/api/jobs/{job_id}/download?filename={f.name}",
                        mime_type=mime
                    ))
                    
            elif tool == "remove-pages":
                if not task_input_paths:
                    raise InvalidFileException("No PDF file uploaded.")
                pages_to_remove = parsed_options.get("pages", [])
                out_path = outputs_dir / f"{task_input_paths[0].stem}_removed_pages.pdf"
                jobs_manager.update_progress(job_id, "Removing", 50, "Removing selected pages...")
                stats = remove_pages(task_input_paths[0], out_path, pages_to_remove)
                output_files.append(OutputFile(
                    filename=out_path.name,
                    size_bytes=out_path.stat().st_size,
                    download_url=f"/api/jobs/{job_id}/download?filename={out_path.name}",
                    mime_type="application/pdf"
                ))
                
            elif tool == "extract-pages":
                if not task_input_paths:
                    raise InvalidFileException("No PDF file uploaded.")
                pages = parsed_options.get("pages", [])
                as_single = parsed_options.get("as_single_pdf", True)
                jobs_manager.update_progress(job_id, "Extracting", 50, "Extracting pages...")
                created = extract_pages(task_input_paths[0], outputs_dir, pages, as_single_pdf=as_single)
                for f in created:
                    mime = "application/zip" if f.suffix == ".zip" else "application/pdf"
                    output_files.append(OutputFile(
                        filename=f.name,
                        size_bytes=f.stat().st_size,
                        download_url=f"/api/jobs/{job_id}/download?filename={f.name}",
                        mime_type=mime
                    ))
                    
            elif tool == "organize-pdf":
                if not task_input_paths:
                    raise InvalidFileException("No PDF file uploaded.")
                actions = parsed_options.get("pages", [])
                out_path = outputs_dir / f"{task_input_paths[0].stem}_organized.pdf"
                jobs_manager.update_progress(job_id, "Organizing", 50, "Applying page ordering and rotations...")
                stats = organize_pdf(task_input_paths[0], out_path, actions)
                output_files.append(OutputFile(
                    filename=out_path.name,
                    size_bytes=out_path.stat().st_size,
                    download_url=f"/api/jobs/{job_id}/download?filename={out_path.name}",
                    mime_type="application/pdf"
                ))
                
            elif tool == "scan-to-pdf":
                if not task_input_paths:
                    raise InvalidFileException("No scanned images provided.")
                out_path = outputs_dir / "scanned_document.pdf"
                jobs_manager.update_progress(job_id, "Compiling", 50, "Compiling scanned pages into PDF...")
                stats = scan_to_pdf(
                    task_input_paths,
                    out_path,
                    page_size=parsed_options.get("page_size", "A4"),
                    orientation=parsed_options.get("orientation", "portrait")
                )
                output_files.append(OutputFile(
                    filename=out_path.name,
                    size_bytes=out_path.stat().st_size,
                    download_url=f"/api/jobs/{job_id}/download?filename={out_path.name}",
                    mime_type="application/pdf"
                ))
                
            # 2. Optimize PDF
            elif tool == "compress-pdf":
                if not task_input_paths:
                    raise InvalidFileException("No PDF file uploaded.")
                out_path = outputs_dir / f"{task_input_paths[0].stem}_compressed.pdf"
                preset = parsed_options.get("preset", "recommended")
                custom_kb = parsed_options.get("custom_target_kb")
                aggressive = parsed_options.get("aggressive", False)
                jobs_manager.update_progress(job_id, "Compressing", 40, "Evaluating compression strategies and candidate outputs...")
                stats = compress_pdf(task_input_paths[0], out_path, preset=preset, custom_target_kb=custom_kb, aggressive=aggressive)
                output_files.append(OutputFile(
                    filename=out_path.name,
                    size_bytes=out_path.stat().st_size,
                    download_url=f"/api/jobs/{job_id}/download?filename={out_path.name}",
                    mime_type="application/pdf",
                    metadata=stats
                ))
                
            elif tool == "repair-pdf":
                if not task_input_paths:
                    raise InvalidFileException("No PDF file uploaded.")
                out_path = outputs_dir / f"{task_input_paths[0].stem}_repaired.pdf"
                jobs_manager.update_progress(job_id, "Repairing", 50, "Attempting structural xref table recovery...")
                stats = repair_pdf(task_input_paths[0], out_path)
                output_files.append(OutputFile(
                    filename=out_path.name,
                    size_bytes=out_path.stat().st_size,
                    download_url=f"/api/jobs/{job_id}/download?filename={out_path.name}",
                    mime_type="application/pdf"
                ))
                
            elif tool == "ocr-pdf":
                if not task_input_paths:
                    raise InvalidFileException("No PDF file uploaded.")
                out_path = outputs_dir / f"{task_input_paths[0].stem}_searchable_ocr.pdf"
                lang = parsed_options.get("language", "eng")
                jobs_manager.update_progress(job_id, "OCR", 50, f"Generating searchable text layer ({lang})...")
                stats = ocr_pdf(task_input_paths[0], out_path, language=lang)
                output_files.append(OutputFile(
                    filename=out_path.name,
                    size_bytes=out_path.stat().st_size,
                    download_url=f"/api/jobs/{job_id}/download?filename={out_path.name}",
                    mime_type="application/pdf"
                ))
                
            # 3. Convert to PDF
            elif tool in ("jpg-to-pdf", "png-to-pdf"):
                if not task_input_paths:
                    raise InvalidFileException("No images uploaded.")
                out_path = outputs_dir / "converted_images.pdf"
                jobs_manager.update_progress(job_id, "Converting", 50, "Converting images to PDF...")
                stats = images_to_pdf(
                    task_input_paths,
                    out_path,
                    page_size=parsed_options.get("page_size", "A4"),
                    orientation=parsed_options.get("orientation", "portrait"),
                    margin=int(parsed_options.get("margin", 20)),
                    fit_mode=parsed_options.get("fit_mode", "contain")
                )
                output_files.append(OutputFile(
                    filename=out_path.name,
                    size_bytes=out_path.stat().st_size,
                    download_url=f"/api/jobs/{job_id}/download?filename={out_path.name}",
                    mime_type="application/pdf"
                ))
                
            elif tool == "word-to-pdf":
                if not task_input_paths:
                    raise InvalidFileException("No Word document uploaded.")
                out_path = outputs_dir / f"{task_input_paths[0].stem}.pdf"
                jobs_manager.update_progress(job_id, "Converting", 50, "Converting Word document to PDF...")
                stats = docx_to_pdf(task_input_paths[0], out_path)
                output_files.append(OutputFile(
                    filename=out_path.name,
                    size_bytes=out_path.stat().st_size,
                    download_url=f"/api/jobs/{job_id}/download?filename={out_path.name}",
                    mime_type="application/pdf"
                ))
                
            elif tool == "powerpoint-to-pdf":
                if not task_input_paths:
                    raise InvalidFileException("No PowerPoint presentation uploaded.")
                out_path = outputs_dir / f"{task_input_paths[0].stem}.pdf"
                jobs_manager.update_progress(job_id, "Converting", 50, "Converting PowerPoint slides to PDF...")
                stats = pptx_to_pdf(task_input_paths[0], out_path)
                output_files.append(OutputFile(
                    filename=out_path.name,
                    size_bytes=out_path.stat().st_size,
                    download_url=f"/api/jobs/{job_id}/download?filename={out_path.name}",
                    mime_type="application/pdf"
                ))
                
            elif tool == "excel-to-pdf":
                if not task_input_paths:
                    raise InvalidFileException("No Excel workbook uploaded.")
                out_path = outputs_dir / f"{task_input_paths[0].stem}.pdf"
                jobs_manager.update_progress(job_id, "Converting", 50, "Converting Excel worksheets to PDF...")
                stats = xlsx_to_pdf(task_input_paths[0], out_path)
                output_files.append(OutputFile(
                    filename=out_path.name,
                    size_bytes=out_path.stat().st_size,
                    download_url=f"/api/jobs/{job_id}/download?filename={out_path.name}",
                    mime_type="application/pdf"
                ))
                
            elif tool == "html-to-pdf":
                raw_html = html_content
                if not raw_html and task_input_paths:
                    with open(task_input_paths[0], "r", encoding="utf-8", errors="ignore") as f:
                        raw_html = f.read()
                if not raw_html:
                    raise InvalidFileException("No HTML content or HTML file provided.")
                out_path = outputs_dir / "converted_webpage.pdf"
                jobs_manager.update_progress(job_id, "Rendering", 50, "Sanitizing HTML and rendering PDF...")
                stats = html_to_pdf(raw_html, out_path)
                output_files.append(OutputFile(
                    filename=out_path.name,
                    size_bytes=out_path.stat().st_size,
                    download_url=f"/api/jobs/{job_id}/download?filename={out_path.name}",
                    mime_type="application/pdf"
                ))
                
            # 4. Convert from PDF
            elif tool == "pdf-to-jpg":
                if not task_input_paths:
                    raise InvalidFileException("No PDF file uploaded.")
                fmt = parsed_options.get("format", "jpg")
                dpi = int(parsed_options.get("dpi", 150))
                pages = parsed_options.get("pages")
                jobs_manager.update_progress(job_id, "Rendering", 50, f"Rendering PDF pages to {fmt.upper()}...")
                created = pdf_to_images(task_input_paths[0], outputs_dir, format=fmt, dpi=dpi, pages=pages)
                for f in created:
                    mime = "application/zip" if f.suffix == ".zip" else ("image/png" if f.suffix == ".png" else "image/jpeg")
                    output_files.append(OutputFile(
                        filename=f.name,
                        size_bytes=f.stat().st_size,
                        download_url=f"/api/jobs/{job_id}/download?filename={f.name}",
                        mime_type=mime
                    ))
                    
            elif tool == "pdf-to-word":
                if not task_input_paths:
                    raise InvalidFileException("No PDF file uploaded.")
                out_path = outputs_dir / f"{task_input_paths[0].stem}.docx"
                jobs_manager.update_progress(job_id, "Converting", 50, "Extracting text structure into Word document...")
                stats = pdf_to_docx(task_input_paths[0], out_path)
                output_files.append(OutputFile(
                    filename=out_path.name,
                    size_bytes=out_path.stat().st_size,
                    download_url=f"/api/jobs/{job_id}/download?filename={out_path.name}",
                    mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                ))
                
            elif tool == "pdf-to-powerpoint":
                if not task_input_paths:
                    raise InvalidFileException("No PDF file uploaded.")
                out_path = outputs_dir / f"{task_input_paths[0].stem}.pptx"
                jobs_manager.update_progress(job_id, "Converting", 50, "Generating PowerPoint presentation slides...")
                stats = pdf_to_pptx(task_input_paths[0], out_path)
                output_files.append(OutputFile(
                    filename=out_path.name,
                    size_bytes=out_path.stat().st_size,
                    download_url=f"/api/jobs/{job_id}/download?filename={out_path.name}",
                    mime_type="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                ))
                
            elif tool == "pdf-to-excel":
                if not task_input_paths:
                    raise InvalidFileException("No PDF file uploaded.")
                out_path = outputs_dir / f"{task_input_paths[0].stem}.xlsx"
                jobs_manager.update_progress(job_id, "Extracting", 50, "Detecting tables and generating Excel workbook...")
                stats = pdf_to_xlsx(task_input_paths[0], out_path)
                output_files.append(OutputFile(
                    filename=out_path.name,
                    size_bytes=out_path.stat().st_size,
                    download_url=f"/api/jobs/{job_id}/download?filename={out_path.name}",
                    mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                ))
                
            elif tool == "pdf-to-pdfa":
                if not task_input_paths:
                    raise InvalidFileException("No PDF file uploaded.")
                out_path = outputs_dir / f"{task_input_paths[0].stem}_pdfa.pdf"
                profile = parsed_options.get("profile", "2b")
                jobs_manager.update_progress(job_id, "Archiving", 50, f"Applying PDF/A-{profile.upper()} standard metadata...")
                stats = pdf_to_pdfa(task_input_paths[0], out_path, profile=profile)
                output_files.append(OutputFile(
                    filename=out_path.name,
                    size_bytes=out_path.stat().st_size,
                    download_url=f"/api/jobs/{job_id}/download?filename={out_path.name}",
                    mime_type="application/pdf"
                ))
                
            # 5. Edit PDF
            elif tool == "rotate-pdf":
                if not task_input_paths:
                    raise InvalidFileException("No PDF file uploaded.")
                out_path = outputs_dir / f"{task_input_paths[0].stem}_rotated.pdf"
                angle = int(parsed_options.get("angle", 90))
                pages = parsed_options.get("pages")
                jobs_manager.update_progress(job_id, "Rotating", 50, f"Rotating pages ({angle}°)...")
                stats = rotate_pdf(task_input_paths[0], out_path, angle=angle, pages=pages)
                output_files.append(OutputFile(
                    filename=out_path.name,
                    size_bytes=out_path.stat().st_size,
                    download_url=f"/api/jobs/{job_id}/download?filename={out_path.name}",
                    mime_type="application/pdf"
                ))
                
            elif tool == "add-page-numbers":
                if not task_input_paths:
                    raise InvalidFileException("No PDF file uploaded.")
                out_path = outputs_dir / f"{task_input_paths[0].stem}_numbered.pdf"
                jobs_manager.update_progress(job_id, "Numbering", 50, "Inserting page numbers...")
                stats = add_page_numbers(
                    task_input_paths[0],
                    out_path,
                    position=parsed_options.get("position", "bottom-center"),
                    format_str=parsed_options.get("format_str", "Page {page} of {total}"),
                    font_size=int(parsed_options.get("font_size", 10)),
                    margin=int(parsed_options.get("margin", 36)),
                    start_number=int(parsed_options.get("start_number", 1)),
                    omit_pages=parsed_options.get("omit_pages", [])
                )
                output_files.append(OutputFile(
                    filename=out_path.name,
                    size_bytes=out_path.stat().st_size,
                    download_url=f"/api/jobs/{job_id}/download?filename={out_path.name}",
                    mime_type="application/pdf"
                ))
                
            elif tool == "add-watermark":
                if not task_input_paths:
                    raise InvalidFileException("No PDF file uploaded.")
                out_path = outputs_dir / f"{task_input_paths[0].stem}_watermarked.pdf"
                img_path = None
                if len(task_input_paths) > 1:
                    img_path = task_input_paths[1]
                jobs_manager.update_progress(job_id, "Watermarking", 50, "Embedding watermark...")
                stats = add_watermark(
                    task_input_paths[0],
                    out_path,
                    watermark_type=parsed_options.get("watermark_type", "text"),
                    text=parsed_options.get("text", "CONFIDENTIAL"),
                    image_path=img_path,
                    opacity=float(parsed_options.get("opacity", 0.3)),
                    rotation=int(parsed_options.get("rotation", 45)),
                    font_size=int(parsed_options.get("font_size", 48)),
                    position=parsed_options.get("position", "center"),
                    pages=parsed_options.get("pages")
                )
                output_files.append(OutputFile(
                    filename=out_path.name,
                    size_bytes=out_path.stat().st_size,
                    download_url=f"/api/jobs/{job_id}/download?filename={out_path.name}",
                    mime_type="application/pdf"
                ))
                
            elif tool == "crop-pdf":
                if not task_input_paths:
                    raise InvalidFileException("No PDF file uploaded.")
                out_path = outputs_dir / f"{task_input_paths[0].stem}_cropped.pdf"
                jobs_manager.update_progress(job_id, "Cropping", 50, "Cropping page bounds...")
                stats = crop_pdf(
                    task_input_paths[0],
                    out_path,
                    x=float(parsed_options.get("x", 0.0)),
                    y=float(parsed_options.get("y", 0.0)),
                    width=float(parsed_options.get("width", 1.0)),
                    height=float(parsed_options.get("height", 1.0)),
                    pages=parsed_options.get("pages")
                )
                output_files.append(OutputFile(
                    filename=out_path.name,
                    size_bytes=out_path.stat().st_size,
                    download_url=f"/api/jobs/{job_id}/download?filename={out_path.name}",
                    mime_type="application/pdf"
                ))
                
            elif tool == "edit-pdf":
                if not task_input_paths:
                    raise InvalidFileException("No PDF file uploaded.")
                out_path = outputs_dir / f"{task_input_paths[0].stem}_edited.pdf"
                annots = parsed_options.get("annotations", [])
                jobs_manager.update_progress(job_id, "Editing", 50, "Embedding annotations onto PDF...")
                stats = edit_pdf(task_input_paths[0], out_path, annots)
                output_files.append(OutputFile(
                    filename=out_path.name,
                    size_bytes=out_path.stat().st_size,
                    download_url=f"/api/jobs/{job_id}/download?filename={out_path.name}",
                    mime_type="application/pdf"
                ))
                
            elif tool == "fill-form":
                if not task_input_paths:
                    raise InvalidFileException("No PDF file uploaded.")
                out_path = outputs_dir / f"{task_input_paths[0].stem}_filled.pdf"
                fields = parsed_options.get("fields", {})
                flatten = parsed_options.get("flatten", False)
                jobs_manager.update_progress(job_id, "Filling", 50, "Updating form field values...")
                stats = fill_pdf_forms(task_input_paths[0], out_path, fields, flatten=flatten)
                output_files.append(OutputFile(
                    filename=out_path.name,
                    size_bytes=out_path.stat().st_size,
                    download_url=f"/api/jobs/{job_id}/download?filename={out_path.name}",
                    mime_type="application/pdf"
                ))
                
            # 6. PDF Security
            elif tool == "unlock-pdf":
                if not task_input_paths:
                    raise InvalidFileException("No PDF file uploaded.")
                password = parsed_options.get("password", "")
                out_path = outputs_dir / f"{task_input_paths[0].stem}_unlocked.pdf"
                jobs_manager.update_progress(job_id, "Decrypting", 50, "Decrypting with provided password...")
                stats = unlock_pdf(task_input_paths[0], out_path, password)
                output_files.append(OutputFile(
                    filename=out_path.name,
                    size_bytes=out_path.stat().st_size,
                    download_url=f"/api/jobs/{job_id}/download?filename={out_path.name}",
                    mime_type="application/pdf"
                ))
                
            elif tool == "protect-pdf":
                if not task_input_paths:
                    raise InvalidFileException("No PDF file uploaded.")
                password = parsed_options.get("password", "")
                out_path = outputs_dir / f"{task_input_paths[0].stem}_protected.pdf"
                jobs_manager.update_progress(job_id, "Encrypting", 50, "Encrypting with AES-256 standard...")
                stats = protect_pdf(
                    task_input_paths[0],
                    out_path,
                    password,
                    allow_printing=parsed_options.get("allow_printing", True),
                    allow_copying=parsed_options.get("allow_copying", True)
                )
                output_files.append(OutputFile(
                    filename=out_path.name,
                    size_bytes=out_path.stat().st_size,
                    download_url=f"/api/jobs/{job_id}/download?filename={out_path.name}",
                    mime_type="application/pdf"
                ))
                
            elif tool == "sign-pdf":
                if not task_input_paths:
                    raise InvalidFileException("No PDF file uploaded.")
                out_path = outputs_dir / f"{task_input_paths[0].stem}_signed.pdf"
                sigs = parsed_options.get("signatures", [])
                jobs_manager.update_progress(job_id, "Signing", 50, "Embedding signature appearance...")
                stats = sign_pdf(task_input_paths[0], out_path, sigs)
                output_files.append(OutputFile(
                    filename=out_path.name,
                    size_bytes=out_path.stat().st_size,
                    download_url=f"/api/jobs/{job_id}/download?filename={out_path.name}",
                    mime_type="application/pdf"
                ))
                
            elif tool == "redact-pdf":
                if not task_input_paths:
                    raise InvalidFileException("No PDF file uploaded.")
                out_path = outputs_dir / f"{task_input_paths[0].stem}_redacted.pdf"
                redactions = parsed_options.get("redactions", [])
                terms = parsed_options.get("search_terms", [])
                jobs_manager.update_progress(job_id, "Redacting", 50, "Irreversibly purging content layers...")
                stats = redact_pdf(task_input_paths[0], out_path, redactions, terms)
                output_files.append(OutputFile(
                    filename=out_path.name,
                    size_bytes=out_path.stat().st_size,
                    download_url=f"/api/jobs/{job_id}/download?filename={out_path.name}",
                    mime_type="application/pdf"
                ))
                
            elif tool == "compare-pdf":
                if len(task_input_paths) < 2:
                    raise InvalidFileException("Two PDF files are required for comparison.")
                jobs_manager.update_progress(job_id, "Comparing", 50, "Comparing text and rendering visual diffs...")
                stats = compare_pdfs(task_input_paths[0], task_input_paths[1], outputs_dir)
                rep_name = stats.get("report_file", "comparison_report.txt")
                zip_name = stats.get("zip_file", "comparison_package.zip")
                
                rep_file = outputs_dir / rep_name
                zip_file = outputs_dir / zip_name
                
                output_files.append(OutputFile(
                    filename=zip_name,
                    size_bytes=zip_file.stat().st_size,
                    download_url=f"/api/jobs/{job_id}/download?filename={zip_name}",
                    mime_type="application/zip",
                    metadata=stats
                ))
                output_files.append(OutputFile(
                    filename=rep_name,
                    size_bytes=rep_file.stat().st_size,
                    download_url=f"/api/jobs/{job_id}/download?filename={rep_name}",
                    mime_type="text/plain",
                    metadata=stats
                ))
                
            # 7. PDF Intelligence
            elif tool == "ai-summarize":
                if not task_input_paths:
                    raise InvalidFileException("No PDF file uploaded.")
                length = parsed_options.get("length", "standard")
                focus = parsed_options.get("focus")
                jobs_manager.update_progress(job_id, "Summarizing", 50, "Extracting text and analyzing document...")
                stats = await summarize_pdf(task_input_paths[0], length=length, focus=focus)
                # Save summary to a text file for download
                summary_file = outputs_dir / f"{task_input_paths[0].stem}_summary.txt"
                with open(summary_file, "w", encoding="utf-8") as f:
                    f.write("=== PaperFlow AI Document Summary ===\n\n")
                    f.write("Executive Summary:\n" + stats.get("summary", "") + "\n\n")
                    f.write("Key Takeaways:\n")
                    for pt in stats.get("key_points", []):
                        f.write(f"- {pt}\n")
                output_files.append(OutputFile(
                    filename=summary_file.name,
                    size_bytes=summary_file.stat().st_size,
                    download_url=f"/api/jobs/{job_id}/download?filename={summary_file.name}",
                    mime_type="text/plain",
                    metadata=stats
                ))
                
            elif tool == "ai-translate":
                if not task_input_paths:
                    raise InvalidFileException("No PDF file uploaded.")
                out_path = outputs_dir / f"{task_input_paths[0].stem}_translated.pdf"
                target_lang = parsed_options.get("target_language", "Spanish")
                jobs_manager.update_progress(job_id, "Translating", 50, f"Translating document into {target_lang}...")
                stats = await translate_pdf(task_input_paths[0], out_path, target_language=target_lang)
                output_files.append(OutputFile(
                    filename=out_path.name,
                    size_bytes=out_path.stat().st_size,
                    download_url=f"/api/jobs/{job_id}/download?filename={out_path.name}",
                    mime_type="application/pdf",
                    metadata=stats
                ))
                
            elif tool == "pdf-to-markdown":
                if not task_input_paths:
                    raise InvalidFileException("No PDF file uploaded.")
                jobs_manager.update_progress(job_id, "Converting", 50, "Extracting text, tables, and images into Markdown...")
                created = pdf_to_markdown(task_input_paths[0], outputs_dir)
                for f in created:
                    mime = "application/zip" if f.suffix == ".zip" else "text/markdown"
                    output_files.append(OutputFile(
                        filename=f.name,
                        size_bytes=f.stat().st_size,
                        download_url=f"/api/jobs/{job_id}/download?filename={f.name}",
                        mime_type=mime
                    ))
                    
            # 8. High-Value New Utilities
            elif tool == "resize-pdf":
                if not task_input_paths:
                    raise InvalidFileException("No PDF file uploaded.")
                out_path = outputs_dir / f"{task_input_paths[0].stem}_resized.pdf"
                target_size = parsed_options.get("target_size", "A4")
                orientation = parsed_options.get("orientation", "portrait")
                fit_content = parsed_options.get("fit_content", True)
                margin = int(parsed_options.get("margin", 18))
                pages = parsed_options.get("pages")
                jobs_manager.update_progress(job_id, "Resizing", 50, f"Resizing page dimensions to {target_size} ({orientation})...")
                stats = resize_pdf(task_input_paths[0], out_path, target_size=target_size, orientation=orientation, fit_content=fit_content, margin=margin, pages=pages)
                output_files.append(OutputFile(
                    filename=out_path.name,
                    size_bytes=out_path.stat().st_size,
                    download_url=f"/api/jobs/{job_id}/download?filename={out_path.name}",
                    mime_type="application/pdf",
                    metadata=stats
                ))
                
            elif tool == "pdf-metadata":
                if not task_input_paths:
                    raise InvalidFileException("No PDF file uploaded.")
                out_path = outputs_dir / f"{task_input_paths[0].stem}_updated_meta.pdf"
                metadata_input = parsed_options.get("metadata", {})
                jobs_manager.update_progress(job_id, "Updating", 50, "Writing document metadata tags...")
                stats = update_pdf_metadata(task_input_paths[0], out_path, metadata_input)
                output_files.append(OutputFile(
                    filename=out_path.name,
                    size_bytes=out_path.stat().st_size,
                    download_url=f"/api/jobs/{job_id}/download?filename={out_path.name}",
                    mime_type="application/pdf",
                    metadata=stats
                ))
                
            elif tool == "extract-text":
                if not task_input_paths:
                    raise InvalidFileException("No PDF file uploaded.")
                out_path = outputs_dir / f"{task_input_paths[0].stem}_extracted_text.txt"
                pages = parsed_options.get("pages")
                jobs_manager.update_progress(job_id, "Extracting", 50, "Extracting plain text layers...")
                stats = extract_text_content(task_input_paths[0], out_path, pages=pages)
                output_files.append(OutputFile(
                    filename=out_path.name,
                    size_bytes=out_path.stat().st_size,
                    download_url=f"/api/jobs/{job_id}/download?filename={out_path.name}",
                    mime_type="text/plain",
                    metadata=stats
                ))
                
            elif tool == "remove-blank-pages":
                if not task_input_paths:
                    raise InvalidFileException("No PDF file uploaded.")
                out_path = outputs_dir / f"{task_input_paths[0].stem}_no_blanks.pdf"
                sensitivity = float(parsed_options.get("sensitivity", 0.992))
                jobs_manager.update_progress(job_id, "Analyzing", 50, "Analyzing text density and visual pixel distribution...")
                stats = remove_blank_pages(task_input_paths[0], out_path, sensitivity=sensitivity)
                output_files.append(OutputFile(
                    filename=out_path.name,
                    size_bytes=out_path.stat().st_size,
                    download_url=f"/api/jobs/{job_id}/download?filename={out_path.name}",
                    mime_type="application/pdf",
                    metadata=stats
                ))
                
            elif tool == "deskew-pdf":
                if not task_input_paths:
                    raise InvalidFileException("No PDF file uploaded.")
                out_path = outputs_dir / f"{task_input_paths[0].stem}_cleaned_deskewed.pdf"
                deskew = parsed_options.get("deskew", True)
                enhance = parsed_options.get("enhance_contrast", True)
                jobs_manager.update_progress(job_id, "Deskewing", 50, "Correcting document skew angle and enhancing contrast...")
                stats = clean_and_deskew_pdf(task_input_paths[0], out_path, deskew=deskew, enhance_contrast=enhance)
                output_files.append(OutputFile(
                    filename=out_path.name,
                    size_bytes=out_path.stat().st_size,
                    download_url=f"/api/jobs/{job_id}/download?filename={out_path.name}",
                    mime_type="application/pdf",
                    metadata=stats
                ))
                
            elif tool == "flatten-form":
                if not task_input_paths:
                    raise InvalidFileException("No PDF file uploaded.")
                out_path = outputs_dir / f"{task_input_paths[0].stem}_flattened.pdf"
                jobs_manager.update_progress(job_id, "Flattening", 50, "Baking form fields and annotations into static content...")
                stats = flatten_pdf_forms(task_input_paths[0], out_path)
                output_files.append(OutputFile(
                    filename=out_path.name,
                    size_bytes=out_path.stat().st_size,
                    download_url=f"/api/jobs/{job_id}/download?filename={out_path.name}",
                    mime_type="application/pdf",
                    metadata=stats
                ))
                
            elif tool == "extract-tables":
                if not task_input_paths:
                    raise InvalidFileException("No PDF file uploaded.")
                out_path = outputs_dir / f"{task_input_paths[0].stem}_tables.xlsx"
                jobs_manager.update_progress(job_id, "Extracting", 50, "Extracting structured tables into Excel workbook...")
                stats = pdf_to_xlsx(task_input_paths[0], out_path)
                output_files.append(OutputFile(
                    filename=out_path.name,
                    size_bytes=out_path.stat().st_size,
                    download_url=f"/api/jobs/{job_id}/download?filename={out_path.name}",
                    mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    metadata=stats
                ))
                    
            else:
                raise InvalidFileException(f"Unrecognized tool '{tool}'.")
                
            jobs_manager.set_completed(job_id, [o.model_dump() for o in output_files], stats=stats)
            
        except Exception as e:
            jobs_manager.set_failed(job_id, str(e))
            
    # Launch async task
    jobs_manager.run_async(job_id, process_task)
    
    return jobs_manager.to_response(job_id)

@router.get("/jobs/{job_id}", response_model=JobResponse)
def get_job_status(job_id: str):
    """Retrieve job status, progress percentages, outputs, or safe error details."""
    return jobs_manager.to_response(job_id)

@router.get("/jobs/{job_id}/download")
def download_job_output(job_id: str, filename: Optional[str] = Query(None)):
    """Download a completed result file."""
    job = jobs_manager.get_job(job_id)
    if job["status"] != JobStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job is not completed yet (current status: {job['status']})."
        )
        
    outputs = storage_service.get_job_outputs(job_id)
    if not outputs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No output files available.")
        
    target_file: Optional[Path] = None
    if filename:
        target_file = storage_service.get_output_file(job_id, filename)
    else:
        # Default to first output
        target_file = outputs[0]
        
    if not target_file or not target_file.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Requested file not found.")
        
    mime_type, _ = mimetypes.guess_type(str(target_file))
    if not mime_type:
        mime_type = "application/octet-stream"
        
    return FileResponse(
        path=str(target_file),
        filename=target_file.name,
        media_type=mime_type,
        headers={"Content-Disposition": f'attachment; filename="{target_file.name}"'}
    )

@router.delete("/jobs/{job_id}")
def cancel_or_delete_job(job_id: str):
    """Cancel an eligible job or delete its files from server workspace."""
    success = jobs_manager.cancel_job(job_id)
    return {"id": job_id, "deleted": success}
