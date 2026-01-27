import pdfplumber
import re

pdf_path = 'DASH Report - ALAKOZAI, MOHAMMAD - 2026-01-20 11-14-10-EST - En.pdf'

with pdfplumber.open(pdf_path) as pdf:
    full_text = ''
    for page in pdf.pages:
        full_text += page.extract_text() + '\n'
    
    # Find Policy #1
    policy1_pos = full_text.find('Policy #1')
    if policy1_pos >= 0:
        # Find next policy or end
        policy2_pos = full_text.find('Policy #2', policy1_pos)
        if policy2_pos < 0:
            policy2_pos = len(full_text)
        
        policy1_section = full_text[policy1_pos:policy2_pos]
        print('=== POLICY #1 SECTION (first 4000 chars) ===')
        print(policy1_section[:4000])
        print('\n\n=== VEHICLE COUNT ===')
        vehicles = re.findall(r'Vehicle\s*#(\d+)', policy1_section, re.IGNORECASE)
        print(f'Found {len(set(vehicles))} unique vehicles: {sorted(set(vehicles))}')
        print(f'\nTotal "Vehicle #" patterns: {len(vehicles)}')
