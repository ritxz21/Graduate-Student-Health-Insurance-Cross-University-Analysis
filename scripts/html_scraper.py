"""
html_scraper.py — Fetch and parse university health insurance web pages.

Public API:
  fetch_page(url)             → (html_text: str, status_code: int)
  extract_visible_text(html)  → str
  find_pdf_links(html, base_url) → list[str]
  scrape_university(uni_dict) → dict with keys 'html_text', 'pdf_urls', 'source_type'
"""

from __future__ import annotations

import re
import time
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from config import REQUEST_HEADERS, REQUEST_DELAY_SECONDS, REQUEST_TIMEOUT_SECONDS

# ---------------------------------------------------------------------------
# Low-level fetch
# ---------------------------------------------------------------------------

def fetch_page(url: str, retries: int = 2) -> tuple[str, int]:
    """
    Fetch a URL and return (html_text, status_code).

    Returns ("", status_code) on failure.
    """
    for attempt in range(retries + 1):
        try:
            resp = requests.get(
                url,
                headers=REQUEST_HEADERS,
                timeout=REQUEST_TIMEOUT_SECONDS,
                allow_redirects=True,
            )
            return resp.text, resp.status_code
        except requests.exceptions.SSLError:
            try:
                resp = requests.get(
                    url,
                    headers=REQUEST_HEADERS,
                    timeout=REQUEST_TIMEOUT_SECONDS,
                    allow_redirects=True,
                    verify=False,
                )
                return resp.text, resp.status_code
            except Exception:
                pass
        except requests.exceptions.RequestException:
            if attempt < retries:
                time.sleep(2)
    return "", 0


# ---------------------------------------------------------------------------
# HTML → text
# ---------------------------------------------------------------------------

# Tags whose content we skip entirely
_SKIP_TAGS = {"script", "style", "nav", "header", "footer", "noscript"}

# Insurance-relevant keyword signals — pages with many of these are more useful
_INSURANCE_KEYWORDS = [
    "premium", "deductible", "copay", "co-pay", "coinsurance",
    "out-of-pocket", "oop", "network", "hmo", "ppo", "epo",
    "mental health", "behavioral health",
    "insurance", "ship", "health plan",
]


def extract_visible_text(html: str) -> str:
    """
    Convert raw HTML to clean visible text, stripping navigation/scripts.

    Returns a normalised string with a single newline between paragraphs.
    """
    soup = BeautifulSoup(html, "lxml")

    # Remove noisy structural elements
    for tag in soup.find_all(_SKIP_TAGS):
        tag.decompose()

    # Prefer main content areas if they exist
    main = (
        soup.find("main")
        or soup.find(id=re.compile(r"(content|main|body)", re.I))
        or soup.find(class_=re.compile(r"(content|main|body)", re.I))
        or soup.body
        or soup
    )

    lines: list[str] = []
    for elem in main.descendants:
        if elem.name in {"p", "li", "td", "th", "h1", "h2", "h3", "h4", "div"}:
            text = elem.get_text(separator=" ", strip=True)
            if text:
                lines.append(text)

    # Deduplicate adjacent identical lines, collapse whitespace
    seen: set[str] = set()
    cleaned: list[str] = []
    for line in lines:
        line = re.sub(r"\s+", " ", line).strip()
        if line and line not in seen:
            seen.add(line)
            cleaned.append(line)

    return "\n".join(cleaned)


def insurance_relevance_score(text: str) -> int:
    """Count how many insurance keywords appear in the text (rough quality gauge)."""
    lower = text.lower()
    return sum(1 for kw in _INSURANCE_KEYWORDS if kw in lower)


# ---------------------------------------------------------------------------
# PDF link discovery
# ---------------------------------------------------------------------------

_PDF_LINK_KEYWORDS = [
    "plan", "insurance", "benefit", "brochure", "summary", "ship",
    "grad", "student", "health",
]


def find_pdf_links(html: str, base_url: str) -> list[str]:
    """
    Return all absolute PDF URLs found in the page.

    Prioritises links whose anchor text or href contains insurance-related terms.
    De-duplicates the result.
    """
    soup = BeautifulSoup(html, "lxml")
    seen: set[str] = set()
    results: list[str] = []

    for tag in soup.find_all("a", href=True):
        href: str = tag["href"].strip()
        abs_url = urljoin(base_url, href)

        if abs_url in seen:
            continue
        seen.add(abs_url)

        # Must look like a PDF
        if not (abs_url.lower().endswith(".pdf") or "pdf" in abs_url.lower()):
            continue

        # Prioritise links that mention insurance-related terms
        anchor_text = tag.get_text(separator=" ", strip=True).lower()
        href_lower = href.lower()
        is_relevant = any(
            kw in anchor_text or kw in href_lower
            for kw in _PDF_LINK_KEYWORDS
        )
        if is_relevant:
            results.insert(0, abs_url)   # put relevant ones first
        else:
            results.append(abs_url)

    return results


# ---------------------------------------------------------------------------
# Download PDFs
# ---------------------------------------------------------------------------

def download_pdf(url: str, save_path: str) -> bool:
    """
    Download a PDF from `url` and save it to `save_path`.

    Returns True on success, False on failure.
    """
    from pathlib import Path

    try:
        resp = requests.get(
            url,
            headers=REQUEST_HEADERS,
            timeout=REQUEST_TIMEOUT_SECONDS,
            stream=True,
        )
        if resp.status_code != 200:
            return False
        content_type = resp.headers.get("Content-Type", "")
        if "pdf" not in content_type.lower() and not url.lower().endswith(".pdf"):
            return False

        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, "wb") as fh:
            for chunk in resp.iter_content(chunk_size=8192):
                fh.write(chunk)
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Determine source_type
# ---------------------------------------------------------------------------

def classify_source_type(html_text: str, pdf_urls: list[str], status_code: int) -> str:
    """
    Classify a page into one of the tracking sheet's source_type values.

    Values: html_only | pdf_primary | html_plus_pdf | portal_gated | third_party_admin
    """
    if status_code in (401, 403) or "login" in html_text.lower()[:500]:
        return "portal_gated"

    third_party_domains = [
        "gallagherstudent.com", "universityhealthplans.com",
        "uhcsr.com", "myschi.com", "academichealthplans.com",
        "aetnastudenthealth.com", "wellfleet", "studentinsurance.com",
    ]
    lower_html = html_text.lower()
    for domain in third_party_domains:
        if domain in lower_html:
            return "third_party_admin"

    has_pdf = bool(pdf_urls)
    # Rough heuristic: if HTML text already has lots of cost data, it's html_plus_pdf or html_only
    score = insurance_relevance_score(extract_visible_text(html_text))
    if score >= 4 and has_pdf:
        return "html_plus_pdf"
    if score >= 4:
        return "html_only"
    if has_pdf:
        return "pdf_primary"
    return "html_only"


# ---------------------------------------------------------------------------
# Top-level scraper for one university
# ---------------------------------------------------------------------------

def scrape_university(uni: dict) -> dict:
    """
    Fetch all source URLs for a university and return a result dict with:
      - 'html_text':   combined visible text from all HTML pages
      - 'pdf_urls':    list of discovered PDF links (not yet downloaded)
      - 'source_type': classified source type string
      - 'status_codes': list of HTTP status codes per URL
      - 'error':       error message if all fetches failed, else None

    Args:
        uni: a university dict from config.UNIVERSITIES

    Returns:
        dict as described above.
    """
    urls: list[str] = [uni["source_url_primary"]]
    secondary = uni.get("source_url_secondary", "")
    if secondary:
        urls += [u.strip() for u in secondary.split(";") if u.strip()]

    all_html_texts: list[str] = []
    all_pdf_urls: list[str] = []
    status_codes: list[int] = []

    for i, url in enumerate(urls):
        if i > 0:
            time.sleep(REQUEST_DELAY_SECONDS)

        html, code = fetch_page(url)
        status_codes.append(code)

        if code == 200 and html:
            visible = extract_visible_text(html)
            all_html_texts.append(visible)
            pdfs = find_pdf_links(html, url)
            for p in pdfs:
                if p not in all_pdf_urls:
                    all_pdf_urls.append(p)

    combined_text = "\n\n---\n\n".join(all_html_texts)
    source_type = classify_source_type(
        all_html_texts[0] if all_html_texts else "",
        all_pdf_urls,
        status_codes[0] if status_codes else 0,
    )

    error = None
    if not combined_text.strip():
        error = f"All fetches returned empty (status codes: {status_codes})"

    return {
        "html_text":    combined_text,
        "pdf_urls":     all_pdf_urls,
        "source_type":  source_type,
        "status_codes": status_codes,
        "error":        error,
    }
