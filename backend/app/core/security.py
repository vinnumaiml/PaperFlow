import re
import os
from pathlib import Path
from typing import Tuple

SAFE_FILENAME_RE = re.compile(r'[^a-zA-Z0-9_\-\.]')

# Known magic bytes signatures
FILE_SIGNATURES = {
    "pdf": [b"%PDF-"],
    "png": [b"\x89PNG\r\n\x1a\n"],
    "jpg": [b"\xff\xd8\xff"],
    "jpeg": [b"\xff\xd8\xff"],
    "webp": [b"RIFF"],
    "docx": [b"PK\x03\x04"],
    "xlsx": [b"PK\x03\x04"],
    "pptx": [b"PK\x03\x04"],
}

def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent directory traversal and filesystem attacks."""
    # Strip paths
    name = os.path.basename(filename).strip()
    # Replace unsafe characters
    cleaned = SAFE_FILENAME_RE.sub("_", name)
    # Ensure not empty and does not begin with a dot
    cleaned = cleaned.lstrip(".")
    if not cleaned:
        cleaned = "unnamed_document"
    # Cap length
    if len(cleaned) > 200:
        base, ext = os.path.splitext(cleaned)
        cleaned = base[: 200 - len(ext)] + ext
    return cleaned

def validate_file_signature(content: bytes, ext: str) -> Tuple[bool, str]:
    """Validate that file content matches expected format header."""
    ext = ext.lower().lstrip(".")
    if not content:
        return False, "File is empty (0 bytes)."
    
    if ext in FILE_SIGNATURES:
        signatures = FILE_SIGNATURES[ext]
        matches = any(content.startswith(sig) for sig in signatures)
        if not matches:
            if ext == "pdf":
                # Some PDFs have comments or whitespace before %PDF-
                if b"%PDF-" in content[:1024]:
                    return True, "Valid"
            return False, f"File signature does not match expected .{ext} format."
    return True, "Valid"

def is_safe_path(base_dir: Path, target_path: Path) -> bool:
    """Ensure target path is strictly inside base_dir to prevent path traversal."""
    try:
        base = base_dir.resolve()
        target = target_path.resolve()
        return base in target.parents or base == target
    except Exception:
        return False
