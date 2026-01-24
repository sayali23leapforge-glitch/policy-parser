#!/usr/bin/env python3
"""
Quick test to see the actual PDF structure, especially claims section
"""
import pdfplumber
import json

pdf_path = r"d:\Auto dashboard\DASH Report - PATEL MEHUL - 2026-01-19 16-20-59-EST - En.pdf"

try:
    with pdfplumber.open(pdf_path) as pdf:
        print(f"📄 PDF has {len(pdf.pages)} pages\n")
        
        # Extract text from all pages
        full_text = ""
        for page_num, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            full_text += f"\n{'='*80}\nPAGE {page_num}\n{'='*80}\n{text}\n"
        
        # Find and print Claims section
        if "Claims" in full_text:
            claims_start = full_text.find("Claims")
            claims_section = full_text[claims_start:claims_start+3000]
            print("\n🔍 CLAIMS SECTION (first 3000 chars):")
            print(claims_section)
            print("\n" + "="*80)
        
        # Find first "Claim #" to see structure
        if "Claim #" in full_text:
            idx = full_text.find("Claim #")
            snippet = full_text[idx:idx+800]
            print("\n🔍 FIRST CLAIM SNIPPET (800 chars):")
            print(repr(snippet))
            print("\nFormatted:")
            print(snippet)

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
