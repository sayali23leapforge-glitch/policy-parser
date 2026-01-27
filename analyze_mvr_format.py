#!/usr/bin/env python3
"""
Analyze the MVR PDF format to understand the structure
"""
import pdfplumber
import sys

pdf_path = r"d:\Auto dashboard\MVR_ON_G0643-37788-00203.pdf"

try:
    with pdfplumber.open(pdf_path) as pdf:
        print(f"=== MVR PDF ANALYSIS ===")
        print(f"Total pages: {len(pdf.pages)}\n")
        
        # Extract text from first 2 pages
        for page_num in range(min(2, len(pdf.pages))):
            page = pdf.pages[page_num]
            text = page.extract_text()
            
            print(f"\n{'='*60}")
            print(f"PAGE {page_num + 1} - FULL TEXT")
            print(f"{'='*60}")
            print(text)
            print(f"{'='*60}\n")
            
            # Show first 1500 characters for analysis
            print(f"\nPAGE {page_num + 1} - FIRST 1500 CHARS (for name extraction):")
            print(text[:1500])
            print(f"\n{'='*60}\n")
            
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
