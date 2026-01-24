#!/usr/bin/env python3
"""Test the PDF parsing with the updated extraction logic"""
import sys
sys.path.insert(0, r'd:\Auto dashboard\backend')

from pdf_parser import parse_dash_pdf

pdf_path = r"d:\Auto dashboard\DASH Report - PATEL MEHUL - 2026-01-19 16-20-59-EST - En.pdf"

print("=" * 80)
print("TESTING PDF PARSING WITH UPDATED LOGIC")
print("=" * 80)

data = parse_dash_pdf(pdf_path)

print("\n" + "=" * 80)
print("CLAIMS EXTRACTED:")
print("=" * 80)

if 'claims' in data and data['claims']:
    for i, claim in enumerate(data['claims'], 1):
        print(f"\n📋 CLAIM #{i}:")
        print(f"  Date: {claim.get('date')}")
        print(f"  At-Fault: {claim.get('fault')}")
        print(f"  Company: {claim.get('company')}")
        print(f"  Status: {claim.get('status')}")
        print(f"  First Party Driver: {claim.get('firstPartyDriver', 'NOT FOUND')}")
        print(f"  Third Party Driver: {claim.get('thirdPartyDriver', 'N/A')}")
        print(f"  Loss: ${claim.get('loss', '0')}")
        print(f"  Expense: ${claim.get('expense', '0')}")
        print(f"  Total: ${claim.get('total', '0')}")
        
        if 'kolItems' in claim and claim['kolItems']:
            print(f"  📊 Loss Details ({len(claim['kolItems'])} items):")
            for item in claim['kolItems']:
                print(f"     • {item['description']}")
                print(f"       Loss: ${item['loss']}, Expense: ${item['expense']}")
else:
    print("❌ No claims found in extraction")

print("\n" + "=" * 80)
