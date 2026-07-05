#!/usr/bin/env python3
"""
parse_piping_pdfs_v2.py (改进版本)

Extract pipeline number(s) and material(s) from each page of PDF piping drawings.
Outputs a CSV (and optionally Excel) with columns:
  pdf_file, page_number, pipeline_numbers, materials, text_snippet

Usage:
  python parse_piping_pdfs_v2.py /path/to/pdf_or_dir output.csv

Dependencies:
  pip install pymupdf pdf2image pytesseract pillow pandas openpyxl regex

System dependency:
  tesseract OCR must be installed (apt, brew, choco, ...).

Notes:
  - Adjust regex patterns below for your drawing conventions (Chinese/English labels).
  - OCR fallback is used when page text is empty.
  - This version includes detailed debugging and error handling.
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
    print("[INFO] OCR is available")
except Exception as e:
    OCR_AVAILABLE = False
    print(f"[WARNING] OCR not available: {e}")

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
    except Exception as e:
        print(f"[ERROR] Failed to extract text: {e}")
        return ""


def ocr_page_image(pdf_path, page_number, dpi=200):
    """Render single page to image and apply pytesseract OCR. page_number is 0-based."""
    if not OCR_AVAILABLE:
        return ""
    try:
        print(f"[DEBUG] Running OCR on page {page_number + 1}...")
        # pdf2image convert_from_path returns PIL images
        images = convert_from_path(str(pdf_path), dpi=dpi, first_page=page_number+1, last_page=page_number+1)
        if not images:
            print(f"[WARNING] No images generated for page {page_number + 1}")
            return ""
        img = images[0]
        try:
            text = pytesseract.image_to_string(img, lang='chi_sim+eng')  # adjust langs if needed
        except Exception:
            text = pytesseract.image_to_string(img)
        return text or ""
    except Exception as e:
        print(f"[ERROR] OCR failed on page {page_number + 1}: {e}")
        return ""


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
    try:
        print(f"[INFO] Opening PDF: {pdf_path}")
        doc = fitz.open(str(pdf_path))
        print(f"[INFO] PDF has {doc.page_count} pages")
        
        for pno in range(doc.page_count):
            print(f"[DEBUG] Processing page {pno + 1}...")
            page = doc.load_page(pno)
            text = extract_text_from_page(page)
            used_ocr = False
            
            if not text or len(text.strip()) < 10:
                print(f"[DEBUG] Page {pno + 1} has no direct text, attempting OCR...")
                # fallback to OCR
                text = ocr_page_image(pdf_path, pno)
                used_ocr = True
            
            pipe_matches = find_all_matches(text, PIPE_PATTERNS)
            mat_matches = find_all_matches(text, MATERIAL_PATTERNS)
            
            print(f"[DEBUG] Page {pno + 1} - Found {len(pipe_matches)} pipes, {len(mat_matches)} materials")
            
            results.append({
                "pdf_file": pdf_path.name,
                "page_number": pno + 1,
                "pipeline_numbers": '; '.join(pipe_matches) if pipe_matches else '',
                "materials": '; '.join(mat_matches) if mat_matches else '',
                "text_snippet": snippet(text, 300),
                "ocr_used": used_ocr
            })
        doc.close()
        print(f"[SUCCESS] Processed {doc.page_count} pages")
    except Exception as e:
        print(f"[ERROR] Failed to process PDF: {e}")
        import traceback
        traceback.print_exc()
    
    return results


def collect_pdfs_from_path(p):
    p = Path(p)
    if p.is_file() and p.suffix.lower() == '.pdf':
        return [p]
    if p.is_dir():
        return sorted([f for f in p.rglob('*.pdf')])
    return []


def main():
    print("=" * 60)
    print("PDF Piping Data Extractor v2.0")
    print("=" * 60)
    
    if len(sys.argv) < 3:
        print("Usage: python parse_piping_pdfs_v2.py /path/to/pdf_or_dir output.csv")
        print("")
        print("Example:")
        print("  python parse_piping_pdfs_v2.py input.pdf ~/Desktop/output.csv")
        sys.exit(1)
    
    src = sys.argv[1]
    out_csv = sys.argv[2]
    
    print(f"[INFO] Input source: {src}")
    print(f"[INFO] Output CSV: {out_csv}")
    print("")
    
    pdfs = collect_pdfs_from_path(src)
    print(f"[INFO] Found {len(pdfs)} PDF file(s)")
    
    if not pdfs:
        print("[ERROR] No PDF files found in", src)
        sys.exit(2)
    
    all_rows = []
    for pdf in pdfs:
        print(f"\n[INFO] Processing file: {pdf.name}")
        try:
            rows = process_pdf(pdf)
            all_rows.extend(rows)
        except Exception as e:
            print(f"[ERROR] Failed to process {pdf}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n[INFO] Total records extracted: {len(all_rows)}")
    
    if all_rows:
        print(f"[INFO] Creating DataFrame...")
        df = pd.DataFrame(all_rows, columns=["pdf_file","page_number","pipeline_numbers","materials","text_snippet","ocr_used"])
        
        print(f"[INFO] Writing CSV to: {out_csv}")
        df.to_csv(out_csv, index=False, encoding='utf-8-sig')
        
        # also write Excel for convenience
        try:
            excel_path = Path(out_csv).with_suffix('.xlsx')
            print(f"[INFO] Writing Excel to: {excel_path}")
            df.to_excel(excel_path, index=False)
            print(f"[SUCCESS] Output generated:")
            print(f"  - CSV: {out_csv}")
            print(f"  - Excel: {excel_path}")
        except Exception as e:
            print(f"[WARNING] Excel export failed: {e}")
            print(f"[SUCCESS] CSV file written: {out_csv}")
    else:
        print("[WARNING] No data extracted from PDF files")
    
    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()
