#!/usr/bin/env python3
"""
Debug script to check what field names Meta is sending
Run this to see the exact field structure from Meta
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app import get_leads_from_meta
import json

print("🔍 Fetching leads from Meta to inspect field names...")
leads = get_leads_from_meta()

if leads:
    print(f"\n✅ Found {len(leads)} leads from Meta\n")
    
    # Check the first lead
    first_lead = leads[0]
    print("📄 First Lead Structure:")
    print(json.dumps(first_lead, indent=2, default=str))
    
    print("\n" + "="*60)
    print("FIELD DATA ANALYSIS:")
    print("="*60)
    
    if 'field_data' in first_lead:
        field_data = first_lead.get('field_data', [])
        print(f"\nFound {len(field_data)} fields in first lead:")
        for i, field in enumerate(field_data, 1):
            field_name = field.get('name', 'N/A')
            field_values = field.get('values', [])
            print(f"\n  {i}. Field Name: '{field_name}'")
            print(f"     Values: {field_values}")
    
    print("\n" + "="*60)
    print("SEARCHING FOR DRIVER LICENSE FIELD:")
    print("="*60)
    
    for lead_idx, lead in enumerate(leads[:3], 1):  # Check first 3 leads
        print(f"\nLead #{lead_idx}:")
        field_data = lead.get('field_data', [])
        found = False
        for field in field_data:
            field_name = field.get('name', '').lower()
            if 'driver' in field_name or 'licence' in field_name or 'license' in field_name or 'g or g2' in field_name:
                field_values = field.get('values', [])
                print(f"  ✅ Found: '{field.get('name')}' = {field_values}")
                found = True
        
        if not found:
            print(f"  ❌ No driver license field found")
            # Show all field names for reference
            all_names = [f.get('name', 'N/A') for f in field_data]
            print(f"     All fields: {all_names}")

else:
    print("❌ No leads found from Meta")
