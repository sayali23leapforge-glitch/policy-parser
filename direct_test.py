#!/usr/bin/env python3
"""Direct test of backend parse endpoint"""
import sys
sys.path.insert(0, 'd:/Auto dashboard/backend')

from pdf_parser import parse_dash_pdf
import glob
import os
import json

# Explicitly search in the workspace directory
workspace_dir = 'd:/Auto dashboard'
search_pattern = os.path.join(workspace_dir, 'DASH Report*.pdf')
pdf_files = sorted(glob.glob(search_pattern), key=os.path.getmtime, reverse=True)

print(f"Searching in: {search_pattern}")
print(f"Found PDFs: {pdf_files}")

if not pdf_files:
    print("❌ No PDFs")
    exit(1)

pdf_path = pdf_files[0]
print(f"Testing: {pdf_path}")

result = parse_dash_pdf(pdf_path)
data = result['data']

print("\n🎯 CRITICAL FIELDS:")
print(f"  VIN: {data.get('vin')}")
print(f"  Vehicle: {data.get('vehicle_year_make_model')}")
print(f"  From Policy: {data.get('extracted_from_policy')}")
print(f"  Name: {data.get('name')}")
