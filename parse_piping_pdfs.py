#!/usr/bin/env python3
"""
parse_piping_pdfs.py

Extract pipeline number(s) and material(s) from each page of PDF piping drawings.
Outputs a CSV (and optionally Excel) with columns:
  pdf_file, page_number, pipeline_numbers, materials, text_snippet

Usage:
  python parse_piping_pdfs.py /path/to/pdf_or_dir output.csv

Dependencies:
  pip install pymupdf pdf2image pytesseract pillow pandas openpyxl regex

System dependency:
  tesseract OCR must be installed (apt, brew, choco, ...).

Notes:
  - Adjust regex patterns below for your drawing conventions (Chinese/English labels).
  - OCR fallback is used when page text is empty.
"""

import sys
import os
import re
import fitz  # PyMuPDF
import pandas as pd
from pathlib import Path

# Optional OCR
try:
    from pdf2image import convert_from_path
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except Exception:
    OCR_AVAILABLE = False

# Regex patterns - tweak to match your drawings
PIPE_PATTERNS = [
    # Chinese common: "管线号: A-101" or "管线号：A-101"
    re.compile(r'管线号[:：]?\s*([A-Za-z0-9\-\_/]+)', re.IGNORECASE),
    # Chinese alternate: "管线："
    re.compile(r'管线[:：]?\s*([A-Za-z0-9\-\_/]+)', re.IGNORECASE),
    # English: "Line No", "Line", "Pipe No", "Line No."
    re.compile(r'(?:Line|Line No|Line No\.|Pipe No|Piping No|Line#)[:：]?\s*([A-Za-z0-9\-\_/]+)', re.IGNORECASE),
    # Generic alphanumeric token often used as line tag (ex: A-101/ L-201)
    re.compile(r'\b([A-Z][A-Z0-9\-_/]{1,20}\d+)\b')
]

MATERIAL_PATTERNS = [
    # Chinese: "材质: SS316" or "材料：碳钢"
    re.compile(r'材质[:：]?\s*([A-Za-z0-9\u4e00-\u9fff\-\s／/]+)', re.IGNORECASE),
    re.compile(r'材料[:：]?\s*([A-Za-z0-9\u4e00-\u9fff\-\s／/]+)', re.IGNORECASE),
    # English: "Material: SS316"
    re.compile(r'Material[:：]?\s*([A-Za-z0-9\-\s/]+)', re.IGNORECASE),
    # Spec or spec. sometimes used
    re.compile(r'Spec[:：]?\s*([A-Za-z0-9\-\s/]+)', re.IGNORECASE),
]


def extract_text_from_page(page):
    """Try direct text extraction via PyMuPDF; return str (may be empty)."""
    try:
        txt = page.get_text("text")
        return txt or ""
    except Exception:
        return ""


def ocr_page_image(pdf_path, page_number, dpi=200):
    """Render single page to image and apply pytesseract OCR. page_number is 0-based."""
    if not OCR_AVAILABLE:
        return ""
    # pdf2image convert_from_path returns PIL images
    images = convert_from_path(str(pdf_path), dpi=dpi, first_page=page_number+1, last_page=page_number+1)
    if not images:
        return ""
    img = images[0]
    try:
        text = pytesseract.image_to_string(img, lang='chi_sim+eng')  # adjust langs if needed
    except Exception:
        text = pytesseract.image_to_string(img)
    return text or ""


def find_all_matches(text, patterns):
    found = []
    for pat in patterns:
        for m in pat.findall(text or ""):
            # If findall returns tuples, take the first group
            if isinstance(m, tuple):
                val = next((g for g in m if g), "")
            else:
                val = m
            val = str(val).strip()
            if val:
                found.append(val)
    # Deduplicate while preserving order
    seen = set()
    out = []
    for v in found:
        if v not in seen:
            seen.add(v)
            out.append(v)
    return out


def snippet(text, length=200):
    s = (text or "").strip().replace('\n', ' ')
    return s[:length] + ('...' if len(s) > length else '')


def process_pdf(pdf_path):
    results = []
    doc = fitz.open(str(pdf_path))
    for pno in range(doc.page_count):
        page = doc.load_page(pno)
        text = extract_text_from_page(page)
        used_ocr = False
        if not text or len(text.strip()) < 10:
            # fallback to OCR
            text = ocr_page_image(pdf_path, pno)
            used_ocr = True
        pipe_matches = find_all_matches(text, PIPE_PATTERNS)
        mat_matches = find_all_matches(text, MATERIAL_PATTERNS)
        results.append({
            "pdf_file": pdf_path.name,
            "page_number": pno + 1,
            "pipeline_numbers": '; '.join(pipe_matches) if pipe_matches else '',
            "materials": '; '.join(mat_matches) if mat_matches else '',
            "text_snippet": snippet(text, 300),
            "ocr_used": used_ocr
        })
    doc.close()
    return results


def collect_pdfs_from_path(p):
    p = Path(p)
    if p.is_file() and p.suffix.lower() == '.pdf':
        return [p]
    if p.is_dir():
        return sorted([f for f in p.rglob('*.pdf')])
    return []


def main():
    if len(sys.argv) < 3:
        print("Usage: python parse_piping_pdfs.py /path/to/pdf_or_dir output.csv")
        sys.exit(1)
    src = sys.argv[1]
    out_csv = sys.argv[2]
    pdfs = collect_pdfs_from_path(src)
    if not pdfs:
        print("No PDF files found in", src)
        sys.exit(2)
    all_rows = []
    for pdf in pdfs:
        print("Processing", pdf)
        try:
            rows = process_pdf(pdf)
            all_rows.extend(rows)
        except Exception as e:
            print("Failed to process", pdf, ":", e)
    df = pd.DataFrame(all_rows, columns=["pdf_file","page_number","pipeline_numbers","materials","text_snippet","ocr_used"])
    df.to_csv(out_csv, index=False, encoding='utf-8-sig')
    # also write Excel for convenience
    try:
        excel_path = Path(out_csv).with_suffix('.xlsx')
        df.to_excel(excel_path, index=False)
        print("Wrote:", out_csv, "and", excel_path)
    except Exception:
        print("Wrote:", out_csv)


if __name__ == "__main__":
    main()
