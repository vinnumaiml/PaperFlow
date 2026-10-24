from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field

class MergeOptions(BaseModel):
    file_order: Optional[List[str]] = None

class SplitOptions(BaseModel):
    mode: str = Field(default="ranges", description="ranges, extract_all, fixed_groups")
    ranges: Optional[str] = Field(default="1", description="e.g. 1-3, 5, 7-10")
    group_size: Optional[int] = 1

class RemovePagesOptions(BaseModel):
    pages: List[int] = Field(description="1-indexed list of page numbers to delete")

class ExtractPagesOptions(BaseModel):
    pages: List[int] = Field(description="1-indexed list of page numbers to extract")
    as_single_pdf: bool = True

class PageAction(BaseModel):
    page_num: int  # 1-indexed original page
    rotation: int = 0  # 0, 90, 180, 270
    duplicate_count: int = 1
    deleted: bool = False

class OrganizeOptions(BaseModel):
    pages: List[PageAction]

class ScanToPdfOptions(BaseModel):
    page_size: str = "A4"  # A4, Letter, Fit
    orientation: str = "portrait"  # portrait, landscape
    auto_rotate: bool = True

class CompressOptions(BaseModel):
    preset: str = Field(default="recommended", description="recommended, smaller_file, high_quality, custom")
    custom_target_kb: Optional[int] = Field(default=None, description="Maximum desired output size in KB")
    aggressive: bool = False

class RotateOptions(BaseModel):
    angle: int = 90  # 90, 180, 270
    pages: Optional[List[int]] = None  # None means all pages

class PageNumbersOptions(BaseModel):
    position: str = "bottom-center"  # bottom-left, bottom-center, bottom-right, top-left, top-center, top-right
    format_str: str = "Page {page} of {total}"
    font_size: int = 10
    margin: int = 36  # points
    start_number: int = 1
    omit_pages: List[int] = Field(default_factory=list)

class WatermarkOptions(BaseModel):
    watermark_type: str = "text"  # text or image
    text: Optional[str] = "CONFIDENTIAL"
    font_size: int = 42
    color: str = "#888888"
    opacity: float = 0.3
    rotation: int = 45
    position: str = "center"  # center, top, bottom
    pages: Optional[List[int]] = None

class CropOptions(BaseModel):
    # Normalized coordinates 0.0 to 1.0 or points
    x: float = 0.0
    y: float = 0.0
    width: float = 1.0
    height: float = 1.0
    pages: Optional[List[int]] = None

class Annotation(BaseModel):
    type: str  # text, highlight, rect, freeline, stamp
    page: int  # 1-indexed
    x: float
    y: float
    width: Optional[float] = None
    height: Optional[float] = None
    text: Optional[str] = None
    color: str = "#000000"
    font_size: Optional[int] = 14
    points: Optional[List[List[float]]] = None

class EditPdfOptions(BaseModel):
    annotations: List[Annotation] = Field(default_factory=list)

class FormFillOptions(BaseModel):
    fields: Dict[str, Any] = Field(default_factory=dict)
    flatten: bool = False

class ProtectOptions(BaseModel):
    password: str
    allow_printing: bool = True
    allow_copying: bool = True

class UnlockOptions(BaseModel):
    password: str

class SignatureItem(BaseModel):
    page: int
    x: float
    y: float
    width: float
    height: float
    image_data: str  # Base64 data URL

class SignOptions(BaseModel):
    signatures: List[SignatureItem]

class RedactionItem(BaseModel):
    page: int
    x: float
    y: float
    width: float
    height: float
    text_search: Optional[str] = None

class RedactOptions(BaseModel):
    redactions: List[RedactionItem] = Field(default_factory=list)
    search_terms: List[str] = Field(default_factory=list)

class CompareOptions(BaseModel):
    diff_mode: str = "visual_and_text"  # visual, text, visual_and_text

class OcrOptions(BaseModel):
    language: str = "eng"

class ConvertImagesOptions(BaseModel):
    page_size: str = "A4"
    orientation: str = "portrait"
    margin: int = 20
    fit_mode: str = "contain"  # contain, fill, original

class ConvertToImagesOptions(BaseModel):
    format: str = "jpg"  # jpg or png
    dpi: int = 150
    pages: Optional[List[int]] = None

class HtmlToPdfOptions(BaseModel):
    page_size: str = "A4"
    orientation: str = "portrait"
    margin_mm: int = 10

class AiSummarizeOptions(BaseModel):
    length: str = "standard"  # short, standard, detailed
    focus: Optional[str] = None

class AiTranslateOptions(BaseModel):
    target_language: str = "Spanish"
