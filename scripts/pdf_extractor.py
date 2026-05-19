"""
pdf_extractor.py — Extract raw text from insurance plan PDFs.

Strategy:
  1. Try pdfplumber first (best for text-layer PDFs).
  2. Fall back to PyPDF2 if pdfplumber returns very little text.
  3. Flag scanned-image PDFs (very low text yield) so they can be manually handled.

Public API:
  extract_text_from_pdf(pdf_path)  → str
  extract_pdf_metadata(pdf_path)   → dict
"""

from __future__ import annotations

import re
from pathlib import Path


# ---------------------------------------------------------------------------
# Thresholds
# ---------------------------------------------------------------------------
MIN_TEXT_CHARS = 100          # below this we consider extraction a failure
SCANNED_PDF_THRESHOLD = 50    # below this we flag as likely scanned image


def _try_pdfplumber(pdf_path: Path) -> str:
    """Extract text using pdfplumber (handles text-layer PDFs well)."""
    try:
        import pdfplumber  # type: ignore

        text_parts: list[str] = []
        with pdfplumber.open(str(pdf_path)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return "\n".join(text_parts)
    except Exception as exc:
        return f"__PDFPLUMBER_ERROR__: {exc}"


def _try_pypdf2(pdf_path: Path) -> str:
    """Extract text using PyPDF2 as a fallback."""
    try:
        from PyPDF2 import PdfReader  # type: ignore

        reader = PdfReader(str(pdf_path))
        text_parts: list[str] = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        return "\n".join(text_parts)
    except Exception as exc:
        return f"__PYPDF2_ERROR__: {exc}"


def extract_text_from_pdf(pdf_path: str | Path) -> str:
    """
    Return all extractable text from a PDF.

    If the PDF appears to be a scanned image (very little text extracted),
    the returned string will start with '__SCANNED_PDF__' as a flag.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        Extracted text string (may be empty or flagged).
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        return f"__FILE_NOT_FOUND__: {pdf_path}"

    text = _try_pdfplumber(pdf_path)

    # If pdfplumber errored or returned very little, try PyPDF2
    if text.startswith("__PDFPLUMBER_ERROR__") or len(text.strip()) < MIN_TEXT_CHARS:
        fallback = _try_pypdf2(pdf_path)
        if not fallback.startswith("__PYPDF2_ERROR__") and len(fallback.strip()) >= len(text.strip()):
            text = fallback

    # Flag scanned-image PDFs
    if len(text.strip()) < SCANNED_PDF_THRESHOLD:
        return f"__SCANNED_PDF__\n{text}"

    return text


def extract_pdf_metadata(pdf_path: str | Path) -> dict:
    """
    Return basic metadata about a PDF (page count, file size, text yield).

    Useful for the extraction log.
    """
    pdf_path = Path(pdf_path)
    result = {
        "file_name":    pdf_path.name,
        "file_size_kb": round(pdf_path.stat().st_size / 1024, 1) if pdf_path.exists() else None,
        "page_count":   None,
        "char_count":   None,
        "scanned":      None,
    }
    try:
        import pdfplumber  # type: ignore

        with pdfplumber.open(str(pdf_path)) as pdf:
            result["page_count"] = len(pdf.pages)

        text = extract_text_from_pdf(pdf_path)
        result["char_count"] = len(text)
        result["scanned"] = text.startswith("__SCANNED_PDF__")
    except Exception:
        pass

    return result


# ---------------------------------------------------------------------------
# Text normalisation helpers used by field_extractors
# ---------------------------------------------------------------------------

def normalise_whitespace(text: str) -> str:
    """Collapse multiple whitespace runs and strip leading/trailing space."""
    return re.sub(r"\s+", " ", text).strip()


def clean_dollar_amount(raw: str) -> int | float | None:
    """
    Convert a raw dollar string like '$3,495.24' or '8,232' to a number.

    Returns an int if there are no cents, float otherwise, or None on failure.
    """
    raw = raw.replace("$", "").replace(",", "").strip()
    try:
        val = float(raw)
        return int(val) if val == int(val) else val
    except ValueError:
        return None
