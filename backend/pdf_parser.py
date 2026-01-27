"""
PDF Parser for MVR and DASH Reports
Extracts relevant driver information from uploaded PDF files
"""
import re
import json
from datetime import datetime
import PyPDF2
from io import BytesIO


def parse_dash_pdf(pdf_file):
    """
    Parse DASH (Driver Abstract/Summary History) PDF and extract driver information
    
    Args:
        pdf_file: File object or bytes of the PDF
        
    Returns:
        dict: Extracted DASH information
    """
    try:
        print("\n[INFO] Starting DASH PDF parsing...")
        # Use pdfplumber for more robust text extraction
        import pdfplumber
        if isinstance(pdf_file, bytes):
            pdf_file = BytesIO(pdf_file)
        full_text = ""
        page_count = 0
        with pdfplumber.open(pdf_file) as pdf:
            print(f"[PDF] PDF has {len(pdf.pages)} pages")
            for page_idx, page in enumerate(pdf.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        full_text += page_text + "\n"
                        page_count += 1
                        print(f"  Page {page_idx + 1}: Extracted {len(page_text)} characters")
                    else:
                        print(f"  Page {page_idx + 1}: No text extracted (possibly scanned image)")
                except Exception as page_error:
                    print(f"  [ERROR] Error extracting text from page {page_idx + 1}: {str(page_error)}")
        
        print(f"[OK] Successfully extracted text from {page_count} page(s), total: {len(full_text)} characters")
        
        if not full_text or len(full_text.strip()) < 50:
            print("[WARNING] Extracted text is too short or empty")
            print(f"First 100 chars: {full_text[:100]}")

        # Parse the extracted text
        print("[PARSE] Calling extract_dash_fields...")
        dash_data = extract_dash_fields(full_text)
        
        print(f"[OK] DASH parsing complete. Extracted fields: {list(dash_data.keys())}")
        
        return {
            "success": True,
            "data": dash_data,
            "raw_text": full_text  # For debugging
        }
    except Exception as e:
        error_msg = f"PDF Parsing Error: {str(e)}"
        print(f"[ERROR] {error_msg}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": error_msg
        }

def extract_dash_fields(text):
    """
    Extract specific fields from DASH text
    """
    data = {}
    print("=== DASH PDF TEXT SAMPLE (First 2000 chars) ===")
    print(text[:2000])
    print("=== END SAMPLE ===")
    report_date_match = re.search(r'Report\s*Date:\s*(\d{4}-\d{1,2}\s*\d{1,2}-\d{1,2})', text, re.IGNORECASE)
    if report_date_match:
        # Remove any spaces from the date
        date_str = report_date_match.group(1).replace(' ', '')
        data['issue_date'] = normalize_date(date_str)
        data['report_date'] = normalize_date(date_str)
        print(f" Found Report Date: {data['report_date']}")
    
    # Driver Name - REMOVED: Name should only come from MVR
    # Name will be extracted from MVR PDF, not from DASH
    
    # Address - format: "Address: 201-1480 Eglinton Ave W ,Toronto,ON M6C2G5"
    address_patterns = [
        r'Address:\s*(.+?)\s+Number of',  # Get everything until "Number of"
        r'Address:\s*([^\n]+)',
    ]
    for pattern in address_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['address'] = match.group(1).strip()
            print(f"Found address: {data['address']}")
            break
    
    # License Number - format: "DLN: G6043-37788-80203"
    license_patterns = [
        r'DLN:\s*([A-Z0-9\-]+)',  # DLN: G6043-37788-80203
        r'License\s*(?:Number|#|No\.?)?[:\s]+([A-Z0-9\-]+)',
        r'DL\s*(?:Number|#)?[:\s]+([A-Z0-9\-]+)',
    ]
    for pattern in license_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['license_number'] = match.group(1).strip()
            break
    
    # Date of Birth - REMOVED: DOB should only come from MVR
    # Date of Birth will be extracted from MVR PDF, not from DASH
    
    # Expiry Date
    expiry_patterns = [
        r'Expir(?:y|ation)\s*Date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'Exp\.?\s*Date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'Valid\s*(?:Through|Until)[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
    ]
    for pattern in expiry_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['expiry_date'] = normalize_date(match.group(1))
            break
    
    # Issue/Renewal Date
    issue_patterns = [
        r'Report\s*Date[:\s]+(\d{4}-\d{2}-\d{2})',  # Report Date: 2025-01-05
        r'Issue\s*Date[:\s]+(\d{4}-\d{2}-\d{2})',
        r'Issue\s*Date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'Issued[:\s]+(\d{4}-\d{2}-\d{2})',
        r'Issued[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'Renewal\s*Date[:\s]+(\d{4}-\d{2}-\d{2})',
        r'Renewal\s*Date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'(?:Issue|Issued)[:\s]+(\d{4}-\d{2}-\d{2})'  # DASH format: 2025-01-05
    ]
    for pattern in issue_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['issue_date'] = normalize_date(match.group(1))
            print(f" Found issue/renewal/report date: {data['issue_date']} (pattern: {pattern[:30]}...)")
            break
    
    if not data.get('issue_date'):
        print("[WARNING] No issue/renewal/report date found in PDF")
    
    # Class
    class_patterns = [
        r'Class[:\s]+([A-Z0-9]+)',
        r'License\s*Class[:\s]+([A-Z0-9]+)'
    ]
    for pattern in class_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['license_class'] = match.group(1).strip()
            break
    
    # VIN and Vehicle info: Extract ALL VEHICLES from Policy #1 section ONLY
    # Find Policy #1, then extract up to Policy #2 (or end if no Policy #2)
    
    policy1_pos = text.find('Policy #1')
    policy1_vehicles_list = []  # Array to store ALL vehicles from Policy #1
    
    print(f"\n[VEHICLES] Searching for 'Policy #1'...")
    print(f"[VEHICLES] policy1_pos = {policy1_pos}")
    print(f"[VEHICLES] Total text length: {len(text)} chars")
    
    # Also search for vehicle section
    vehicle_search = text.find('Vehicle #')
    print(f"[VEHICLES] Searching for 'Vehicle #'... found at position: {vehicle_search}")
    
    if vehicle_search >= 0:
        print(f"[VEHICLES] Vehicle section found! Text around it (500 chars):")
        start = max(0, vehicle_search - 100)
        end = min(len(text), vehicle_search + 400)
        print(f"{text[start:end]}")
    else:
        print(f"[VEHICLES] ❌ NO 'Vehicle #' found in entire PDF text!")
        print(f"[VEHICLES] Searching for alternative vehicle patterns...")
        
        # Check for other possible patterns
        if 'VIN' in text:
            print(f"[VEHICLES] Found 'VIN' in text")
            vin_pos = text.find('VIN')
            print(f"[VEHICLES] Text around VIN (300 chars):")
            start = max(0, vin_pos - 100)
            end = min(len(text), vin_pos + 200)
            print(f"{text[start:end]}")
        
        if 'VEHICLE' in text.upper():
            print(f"[VEHICLES] Found 'VEHICLE' (uppercase) in text")
            veh_pos = text.upper().find('VEHICLE')
            print(f"[VEHICLES] Text around VEHICLE (300 chars):")
            start = max(0, veh_pos - 100)
            end = min(len(text), veh_pos + 200)
            print(f"{text[start:end]}")
    
    if policy1_pos >= 0:
        # Find the NEXT policy number after Policy #1
        # Search from after "Policy #1" to find "Policy #2", "Policy #3", etc.
        remaining_text = text[policy1_pos + len('Policy #1'):]
        
        next_policy_match = re.search(r'Policy\s*#(\d+)', remaining_text)
        
        if next_policy_match:
            # Policy #1 section ends where the next policy begins
            next_policy_pos = policy1_pos + len('Policy #1') + next_policy_match.start()
            policy1_section = text[policy1_pos:next_policy_pos]
            print(f"[VEHICLES] Found next policy, Policy #1 section size: {len(policy1_section)} chars")
        else:
            # No next policy, take the rest of the document
            policy1_section = text[policy1_pos:]
            print(f"[VEHICLES] No next policy found, taking rest of doc. Policy #1 section size: {len(policy1_section)} chars")
        
        print(f"[VEHICLES] Policy #1 section (first 1000 chars):\n{policy1_section[:1000]}")
        print(f"[VEHICLES] ...")
        print(f"[VEHICLES] Policy #1 section (last 500 chars):\n{policy1_section[-500:]}")
        
        # Extract ALL vehicles from Policy #1 by finding all "Vehicle #N:" patterns
        # Split by any Vehicle #N pattern to get all vehicle blocks
        vehicle_blocks = re.split(r'Vehicle\s*#(\d+):\s*', policy1_section, flags=re.IGNORECASE)
        
        print(f"[VEHICLES] Split result: {len(vehicle_blocks)} blocks")
        if len(vehicle_blocks) > 1:
            print(f"[VEHICLES] vehicle_blocks structure: {[type(b).__name__ + f'(len={len(b)})' for b in vehicle_blocks[:5]]}")
        else:
            print(f"[VEHICLES] ❌ No Vehicle #N pattern matched! Regex didn't split anything")
        
        # vehicle_blocks will be: ['text_before', 'num1', 'content1', 'num2', 'content2', ...]
        # Process pairs: (vehicle_number, vehicle_content)
        
        for i in range(1, len(vehicle_blocks), 2):
            if i + 1 < len(vehicle_blocks):
                vehicle_num = vehicle_blocks[i].strip()
                block = vehicle_blocks[i + 1]
                
                print(f"[VEHICLES] Processing Vehicle #{vehicle_num}...")
                print(f"[VEHICLES]   Block content (first 200 chars): {block[:200]}")
                
                # Check if this block contains a VIN (17-char code)
                vin_match = re.search(r'([A-HJ-NPR-Z0-9]{17})', block)
                
                if vin_match and not re.match(r'^(Principal Operator|Named Insured|Self|Spouse)', block.strip(), re.IGNORECASE):
                    # This block has a VIN and is not just a role label
                    vin = vin_match.group(1).strip().upper()
                    
                    # Extract year/make/model - everything up to the VIN
                    vehicle_line = block[:vin_match.start()].strip()
                    
                    # Take only the first line
                    lines = vehicle_line.split('\n')
                    vehicle_info = lines[0].strip() if lines else vehicle_line
                    
                    # Clean up the text
                    vehicle_info = re.sub(r'\s+', ' ', vehicle_info)  # collapse whitespace
                    vehicle_info = vehicle_info.rstrip(' -/').strip()   # remove trailing separators
                    
                    # Skip if it's empty or just a role
                    if vehicle_info and not re.match(r'^(Principal Operator|Named Insured|Self|Spouse|DLN|Ontario|Relationship)', vehicle_info, re.IGNORECASE):
                        policy1_vehicles_list.append({
                            'vehicle_number': vehicle_num,
                            'vin': vin,
                            'year_make_model': vehicle_info
                        })
                        print(f"[VEHICLES] ✅ Found Vehicle #{vehicle_num}: {vehicle_info} | VIN: {vin}")
                else:
                    print(f"[VEHICLES] ❌ No valid VIN found in block or block is role label")
        
        if not policy1_vehicles_list:
            print("[VEHICLES] ❌ No vehicles with VIN found in Policy #1 section")
    else:
        print("[VEHICLES] ❌ Policy #1 not found in PDF")
    
    print(f"[VEHICLES] FINAL RESULT: {len(policy1_vehicles_list)} vehicles extracted")
    print(f"[VEHICLES] policy1_vehicles_list = {policy1_vehicles_list}")
    
    # Store all vehicles from Policy #1 for frontend to render
    data['policy1_vehicles'] = policy1_vehicles_list
    
    # For backward compatibility, set single vehicle fields (use first vehicle if available)
    if policy1_vehicles_list:
        data['vin'] = policy1_vehicles_list[0]['vin']
        data['vehicle_year_make_model'] = policy1_vehicles_list[0]['year_make_model']
    else:
        data['vin'] = '-'
        data['vehicle_year_make_model'] = '-'
    
    data['extracted_from_policy'] = '1'  # Indicates this is from Policy #1
    
    # Years of Continuous Insurance
    cont_ins_match = re.search(r'Years\s+of\s+Continuous\s+Insurance:\s*(\d+)', text, re.IGNORECASE)
    if cont_ins_match:
        data['years_continuous_insurance'] = cont_ins_match.group(1)
        print(f" Years of Continuous Insurance: {data['years_continuous_insurance']}")
    
    # Policy dates for gap calculation
    # Find all policies in the Policies section: "#1 2025-08-08 to 2026-08-08 ..."
    policies_section_match = re.search(r'Policies\s*\n(.*?)(?:Claims|Page \d+ of \d+|$)', text, re.DOTALL | re.IGNORECASE)
    if policies_section_match:
        policies_text = policies_section_match.group(1)
        # Extract all policies with pattern: #N YYYY-MM-DD to YYYY-MM-DD
        policy_pattern = r'#(\d+)\s+(\d{4}-\d{1,2}-\d{1,2})\s+to\s+(\d{4}-\d{1,2}-\d{1,2})'
        policy_matches = list(re.finditer(policy_pattern, policies_text))
        
        if policy_matches:
            # Store ALL policies for gap calculation
            # IMPORTANT: Preserve the order from the PDF (data source) - DO NOT SORT
            all_policies = []
            for match in policy_matches:
                policy = {
                    'number': int(match.group(1)),
                    'start_date': normalize_date(match.group(2).replace(' ', '')),
                    'end_date': normalize_date(match.group(3).replace(' ', ''))
                }
                all_policies.append(policy)
            
            # STRICT REQUIREMENT: DO NOT SORT - use order provided by data source
            # The order of appearance in the PDF is the only source of truth
            data['all_policies'] = all_policies
            print(f" Extracted {len(all_policies)} policies in PDF order (NO SORTING)")
            
            # Get the FIRST policy from the PDF (not necessarily Policy #1)
            first_policy_data = all_policies[0]
            
            # First insurance = start date of first policy in the list
            data['first_insurance_date'] = first_policy_data['start_date']
            
            # Renewal date = first policy's expiry date
            data['renewal_date'] = first_policy_data['end_date']
            
            # Policy end date = first policy's expiry date
            data['policy_end_date'] = first_policy_data['end_date']
            
            # Get the LAST policy (current/latest one) for policy_start_date
            last_policy_data = all_policies[-1]
            data['policy_start_date'] = last_policy_data['start_date']
            
            print(f" First Insurance Date (from first policy in list): {data['first_insurance_date']}")
            print(f" Renewal Date (First policy Expiry): {data['renewal_date']}")
            print(f" Current Policy Start Date (from last policy): {data['policy_start_date']}")

    
    # Fallback: Try to get from detail section if policies section not found
    if not data.get('policy_start_date'):
        earliest_term_match = re.search(r'Start\s+of\s+the\s+Earliest\s+Term:\s*(\d{4}-\d{2}-\d{2})', text)
        if earliest_term_match:
            data['policy_start_date'] = normalize_date(earliest_term_match.group(1))
            print(f" Policy Start Date (fallback): {data['policy_start_date']}")
    
    if not data.get('policy_end_date'):
        latest_term_match = re.search(r'End\s+of\s+the\s+Latest\s+Term:\s*(\d{4}-\d{2}-\d{2})', text)
        if latest_term_match:
            data['policy_end_date'] = normalize_date(latest_term_match.group(1))
            print(f" Policy End Date (fallback): {data['policy_end_date']}")
    
    # Status
    status_patterns = [
        r'Status[:\s]+(Valid|Active|Suspended|Revoked|Expired)',
        r'License\s*Status[:\s]+(Valid|Active|Suspended|Revoked|Expired)'
    ]
    for pattern in status_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['license_status'] = match.group(1).strip()
            break
    
    # Demerit Points
    points_patterns = [
        r'(?:Demerit\s*)?Points?[:\s]+(\d+)',
        r'Point\s*Balance[:\s]+(\d+)',
        r'Current\s*Points[:\s]+(\d+)'
    ]
    for pattern in points_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['demerit_points'] = match.group(1)
            break
    
    # Conditions/Restrictions
    conditions_match = re.search(r'Conditions?[:\s]+([^\n]+)', text, re.IGNORECASE)
    if conditions_match:
        data['conditions'] = conditions_match.group(1).strip()
    
    # Claims History - extract ONLY from the "Claims" section
    # NOT from the "Policies" section
    claims = []
    
    print("\n=== EXTRACTING CLAIMS ===")
    
    # Find the "Claims" section in the PDF - improved to capture all claims across pages
    # Look for Claims section and capture until "Previous Inquiries" section
    claims_section_match = re.search(r'Claims\s*\n(.*?)(?:Previous Inquiries)', text, re.DOTALL | re.IGNORECASE)
    
    # If not found, try alternative: capture from Claims to end of document
    if not claims_section_match:
        claims_section_match = re.search(r'Claims\s*\n(.*?)$', text, re.DOTALL | re.IGNORECASE)
    
    if claims_section_match:
        claims_text = claims_section_match.group(1)
        print(f"\n=== CLAIMS SECTION ({len(claims_text)} chars) ===")
        print(f"First 1000 chars:\n{claims_text[:1000]}")
        
        # Count potential claim markers
        claim_num_markers = re.findall(r'#(\d+)', claims_text)
        print(f"\n[DEBUG] Found claim number markers: {claim_num_markers}")
        print(f"[DEBUG] Total markers found: {len(claim_num_markers)}")
        
        # Strategy: Split by claim numbers and extract data from each section
        print(f"\n[EXTRACT] Splitting by claim number patterns...")
        
        # Split by # followed by digit
        parts = re.split(r'(?=#\d)', claims_text)
        claim_matches = []
        
        for part_idx, part in enumerate(parts):
            part = part.strip()
            if not part or not part.startswith('#'):
                continue
                
            # Extract claim number
            num_match = re.match(r'#(\d+)', part)
            if not num_match:
                continue
                
            claim_num = num_match.group(1)
            print(f"\n[CLAIM {claim_num}] Processing...")
            print(f"[CLAIM {claim_num}] TEXT PREVIEW: {part[:800]}")  # DEBUG: Show first 800 chars
            
            # Extract date of loss
            date_match = re.search(r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})', part)
            loss_date = date_match.group(1) if date_match else "0000-00-00"
            print(f"  Date: {loss_date}")
            
            # Extract at-fault percentage
            fault_match = re.search(r'At-?Fault\s*:\s*(\d+)\s*%', part, re.IGNORECASE)
            at_fault_pct = fault_match.group(1) if fault_match else "0"
            print(f"  At-Fault: {at_fault_pct}%")
            
            # Extract company name (usually between Date and At-Fault)
            company_match = re.search(rf'#{claim_num}\s+.*?(\d{{4}}[-/]\d{{1,2}}[-/]\d{{1,2}})\s+(.*?)(?:At-?Fault|$)', part, re.IGNORECASE | re.DOTALL)
            company = company_match.group(2).strip() if company_match else ""
            if company:
                company = company.split('\n')[0].strip()  # Take first line only
            print(f"  Company: {company}")
            
            # Create a match-like object to maintain compatibility
            class PartMatch:
                def __init__(self, num, date, company, fault, full_text):
                    self._num = num
                    self._date = date
                    self._company = company
                    self._fault = fault
                    self._text = full_text
                def group(self, idx):
                    if idx == 0: return self._text
                    elif idx == 1: return self._num
                    elif idx == 2: return self._date
                    elif idx == 3: return self._company
                    elif idx == 4: return self._fault
                    return None
                def groups(self):
                    return (self._num, self._date, self._company, self._fault)
                def end(self):
                    return len(self._text)
            
            claim_matches.append(PartMatch(claim_num, loss_date, company, at_fault_pct, part))
        
        print(f"\n[EXTRACT] Total claims extracted: {len(claim_matches)}")
        print(f"[EXTRACT] Expected: {len(claim_num_markers)}, Found: {len(claim_matches)}")
        
        total_claims_found = len(claim_matches)
        print(f"\n[CLAIMS] TOTAL FOUND: {total_claims_found}")
        
        for idx, match in enumerate(claim_matches, 1):
            claim = {}
            print(f"\n[CLAIM {idx}/{total_claims_found}] Processing...")
            claim_num = match.group(1)
            loss_date = match.group(2)
            
            # Extract company name and at-fault percentage
            if len(match.groups()) >= 4:
                # We have the full match with company and at-fault
                company_and_notes = match.group(3).strip()
                at_fault_pct = match.group(4)
                print(f"  [FULL] Company='{company_and_notes}', AtFault={at_fault_pct}%")
            else:
                # Fallback: extract from text after the loss date
                company_and_notes = ""
                at_fault_pct = "0"
                # Try to find at-fault percentage in the text following this claim
                search_start = match.end()
                search_end = min(search_start + 200, len(claims_text))
                next_section = claims_text[search_start:search_end]
                at_fault_match = re.search(r'At-?Fault\s*:\s*(\d+)\s*%', next_section, re.IGNORECASE)
                if at_fault_match:
                    at_fault_pct = at_fault_match.group(1)
                    # Extract company from between loss date and at-fault
                    company_section = next_section[:at_fault_match.start()]
                    company_and_notes = company_section.strip()
                    print(f"  [PARTIAL] Company='{company_and_notes}', AtFault={at_fault_pct}%")
            
            claim['date'] = normalize_date(loss_date)
            
            # Extract FIRST PARTY DRIVER NAME
            # In DASH reports, look for "First Party Driver:" label followed by the name
            # Search in the current claim section first, then in the full PDF text
            first_party_driver = ''
            first_party_match = re.search(r'First\s+Party\s+Driver\s*:\s*([A-Z][A-Za-z\s\-\']+(?:,\s*[A-Z][A-Za-z\s\-\']+)?)', part, re.IGNORECASE)
            if first_party_match:
                first_party_driver = first_party_match.group(1).strip()
            else:
                # If not found in claim section, search the full PDF text around this claim date
                # Create a pattern to find the claim by date and extract details after it
                claim_detail_pattern = rf'Claim\s*#[:\s]*{claim_num}\s+Date\s+of\s+Loss\s+{re.escape(loss_date)}.*?First\s+Party\s+Driver\s*:\s*([A-Z][A-Za-z\s\-\']+(?:,\s*[A-Z][A-Za-z\s\-\']+)?)'
                full_match = re.search(claim_detail_pattern, text, re.DOTALL | re.IGNORECASE)
                if full_match:
                    first_party_driver = full_match.group(1).strip()
                    # Clean up - remove anything after newline or extra content
                    first_party_driver = first_party_driver.split('\n')[0].strip()
                    # Also remove trailing text like "DLN" if it got included
                    first_party_driver = re.sub(r'\s+(DLN|Date\s+of|Listed|Excl|Convict).*$', '', first_party_driver, flags=re.IGNORECASE)
            
            # Clean up the name - remove newlines and extra whitespace
            first_party_driver = first_party_driver.split('\n')[0].strip() if first_party_driver else ''
            first_party_driver = re.sub(r'\s+(DLN|Date\s+of|Listed|Excl|Convict).*$', '', first_party_driver, flags=re.IGNORECASE)
            
            if first_party_driver:
                claim['firstPartyDriver'] = first_party_driver
                print(f"  [FOUND] First Party Driver: {first_party_driver}")
            else:
                print(f"  [NOT FOUND] First Party Driver")
            
            # Extract company name and check for THIRD PARTY indicator
            company = re.sub(r'\*.*?\*', '', company_and_notes).strip()
            claim['company'] = company
            
            # Extract THIRD PARTY DRIVER NAME
            # If company contains "*THIRD PARTY*" or similar, extract the third party name
            third_party_match = re.search(r'\*?THIRD\s*PARTY\*?\s*[-:\s]*([A-Z][A-Z\s\-\']+,\s*[A-Z][A-Za-z\s\-\']+)?', company_and_notes, re.IGNORECASE)
            if third_party_match and third_party_match.group(1):
                claim['thirdPartyDriver'] = third_party_match.group(1).strip()
                print(f"  Third Party Driver: {claim['thirdPartyDriver']}")
            elif re.search(r'\*?THIRD\s*PARTY\*?', company_and_notes, re.IGNORECASE):
                # Third party claim but no explicit name extracted, use company as fallback
                claim['thirdPartyDriver'] = company.replace('*THIRD PARTY*', '').strip() or 'Third Party'
                print(f"  Third Party Driver (from company): {claim['thirdPartyDriver']}")
            
            
            # At-fault
            if at_fault_pct == '0':
                claim['fault'] = 'No'
            elif at_fault_pct == '100':
                claim['fault'] = 'Yes'
            else:
                claim['fault'] = f'{at_fault_pct}%'
            
            # Try to find claim details in the detailed section below
            # Look for the specific claim number section and extract financial details
            claim_detail_pattern = rf'Claim #{claim_num}\s+Date of Loss\s+\d{{4}}-\d{{2}}-\d{{2}}.*?Total Loss:\s*\$\s*([\d,\.]+).*?Total Expense:\s*\$\s*([\d,\.]+)'
            detail_match = re.search(claim_detail_pattern, text, re.DOTALL | re.IGNORECASE)
            
            if detail_match:
                loss_val = detail_match.group(1).replace(',', '').strip()
                expense_val = detail_match.group(2).replace(',', '').strip()
                
                claim['loss'] = loss_val
                claim['expense'] = expense_val
                
                # Calculate total
                try:
                    total = float(loss_val) + float(expense_val)
                    claim['total'] = f'{total:.2f}'
                    print(f"  -> Financials: Loss=${loss_val}, Expense=${expense_val}, Total=${total:.2f}")
                except ValueError:
                    print(f"  [WARNING] Could not calculate total for claim #{claim_num}")
                
                # Extract KOL (claim loss details) items like "KOL16 - Other Property Damage..."
                # Pattern: KOL## - Description: $X (Loss); $Y (Expense);
                # Search in the current claim section and the full PDF
                kol_matches = []
                
                # Improved regex to handle variations in spacing and newlines
                # Match KOL## followed by description, then amounts
                kol_pattern = r'(KOL\d+\s*[-–]\s*[^\n:]+?):\s*\$\s*([\d,\.]+)\s*\(Loss\);\s*\$\s*([\d,\.]+)\s*\(Expense\);'
                kol_matches = re.findall(kol_pattern, part, re.IGNORECASE)
                
                # If not found in claim section, search full PDF for this specific claim's details
                if not kol_matches:
                    # Search a large area around the claim number to find KOL items
                    # Look for "Claim #X" and capture everything until the next "Claim #" or end of document
                    claim_section_pattern = rf'Claim\s*#\s*{claim_num}.*?(?=Claim\s*#\d+|Convictions|$)'
                    claim_section_match = re.search(claim_section_pattern, text, re.DOTALL | re.IGNORECASE)
                    if claim_section_match:
                        claim_section_text = claim_section_match.group(0)
                        kol_matches = re.findall(kol_pattern, claim_section_text, re.IGNORECASE)
                
                if kol_matches:
                    kol_items = []
                    for kol_desc, kol_loss, kol_expense in kol_matches:
                        # Clean up description - remove extra whitespace and newlines
                        clean_desc = ' '.join(kol_desc.split())
                        kol_items.append({
                            'description': clean_desc.strip(),
                            'loss': kol_loss.strip(),
                            'expense': kol_expense.strip()
                        })
                    claim['kolItems'] = kol_items
                    print(f"  -> Found {len(kol_items)} loss detail items (KOL)")
                    for item in kol_items:
                        print(f"     • {item['description']}: ${item['loss']} (Loss), ${item['expense']} (Expense)")
                else:
                    print(f"  -> No loss detail items (KOL) found for this claim")
            else:
                print(f"  [WARNING] No financial details found for claim #{claim_num}")
            
            # Try to find claim status
            status_pattern = rf'Claim #{claim_num}.*?Claim\s*Status:\s*(\w+)'
            status_match = re.search(status_pattern, text, re.DOTALL | re.IGNORECASE)
            if status_match:
                claim['status'] = status_match.group(1).strip()
            else:
                claim['status'] = 'Closed'  # Default if not found
            
            print(f" Claim #{claim_num}: {claim['date']}, Company={claim['company']}, At-Fault={claim['fault']}, Status={claim.get('status', 'N/A')}")
            claims.append(claim)
    else:
        print("[WARNING] No 'Claims' section found in PDF")
    
    print(f"\n FINAL: {len(claims)} claims extracted from Claims section")
    
    if claims:
        data['claims'] = claims
        data['claims_count'] = str(len(claims))
        print(f" Returning {len(claims)} valid claims\n")
    else:
        data['claims'] = []
        data['claims_count'] = '0'
        print(f"[INFO] No valid claims found in PDF\n")
    
    # Email
    email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    if email_match:
        data['email'] = email_match.group(0)
    
    # Phone number - if present
    phone_patterns = [
        r'Phone[:\s]+(\+?[\d\-\(\)\s]+)',
        r'Tel[:\s]+(\+?[\d\-\(\)\s]+)',
        r'Mobile[:\s]+(\+?[\d\-\(\)\s]+)'
    ]
    for pattern in phone_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['phone'] = match.group(1).strip()
            print(f"Found phone: {data['phone']}")
            break
    
    # Email - if present
    email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    if email_match:
        data['email'] = email_match.group(0)
        print(f"Found email: {data['email']}")
    
    # Extract Policy #1 Expiry Date from the policy detail section (NOT the "to" date from policies list)
    # The "to" date might be the cancellation date, but "Expiry Date:" is the actual expiry
    if policy1_pos >= 0:
        # Get Policy #1 section
        remaining_text = text[policy1_pos + len('Policy #1'):]
        next_policy_match = re.search(r'Policy\s*#(\d+)', remaining_text)
        
        if next_policy_match:
            next_policy_pos = policy1_pos + len('Policy #1') + next_policy_match.start()
            policy1_section = text[policy1_pos:next_policy_pos]
        else:
            policy1_section = text[policy1_pos:]
        
        # Look for "Expiry Date: YYYY-MM-DD" or "Expiry Date: MM/DD/YYYY"
        expiry_date_patterns = [
            r'Expiry\s*Date:\s*(\d{4}-\d{1,2}-\d{1,2})',  # YYYY-MM-DD format
            r'Expiry\s*Date:\s*(\d{1,2}/\d{1,2}/\d{4})',  # MM/DD/YYYY format
        ]
        
        policy1_expiry_found = False
        for pattern in expiry_date_patterns:
            expiry_match = re.search(pattern, policy1_section, re.IGNORECASE)
            if expiry_match:
                policy1_expiry_date = normalize_date(expiry_match.group(1))
                data['renewal_date'] = policy1_expiry_date
                policy1_expiry_found = True
                print(f" Found Policy #1 Expiry Date: {policy1_expiry_date}")
                print(f" Updated Renewal Date to Policy #1 Expiry Date: {data['renewal_date']}")
                break
        
        if not policy1_expiry_found:
            print(f" Policy #1 Expiry Date not found in policy detail section, using policy list end_date")
    
    # Log what was extracted
    extracted_fields = [k for k, v in data.items() if v]
    print(f"\n[OK] DASH extraction complete:")
    print(f"  Fields extracted: {extracted_fields}")
    print(f"  Total fields with values: {len(extracted_fields)} out of {len(data)}")
    print(f"=== DASH EXTRACTED DATA ===")
    print(json.dumps(data, indent=2, default=str))
    print(f"=== END DATA ===")
    
    if not extracted_fields:
        print("\n[WARNING] WARNING: No fields were extracted from the PDF text!")
        print("This could mean:")
        print("  1. PDF is image-based/scanned (needs OCR)")
        print("  2. Text layout doesn't match expected patterns")
        print("  3. PDF is corrupted")
    
    return data


def parse_mvr_pdf(pdf_file):
    """
    Parse MVR PDF and extract driver information
    
    Args:
        pdf_file: File object or bytes of the PDF
        
    Returns:
        dict: Extracted MVR information
    """
    try:
        # Read PDF
        if isinstance(pdf_file, bytes):
            pdf_file = BytesIO(pdf_file)
        
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        # Extract text from all pages
        full_text = ""
        for page in pdf_reader.pages:
            full_text += page.extract_text() + "\n"
        
        # Parse the extracted text
        mvr_data = extract_mvr_fields(full_text)
        
        # CRITICAL: Verify policy1_vehicles is in the response
        print(f"\n[PARSE_MVR] Verifying response data:")
        print(f"[PARSE_MVR] - 'policy1_vehicles' in mvr_data: {'policy1_vehicles' in mvr_data}")
        if 'policy1_vehicles' in mvr_data:
            print(f"[PARSE_MVR] - mvr_data['policy1_vehicles']: {mvr_data['policy1_vehicles']}")
        
        return {
            "success": True,
            "data": mvr_data,
            "raw_text": full_text  # For debugging
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def extract_mvr_fields(text):
    """
    Extract specific fields from MVR text using regex patterns
    """
    data = {}
    
    print("=== MVR PDF TEXT SAMPLE (First 2000 chars) ===")
    print(text[:2000])
    print("=== END SAMPLE ===")
    
    # Extract text before DOB to search for name (names usually come before DOB)
    dob_pos = text.find('Birth Date')
    if dob_pos < 0:
        dob_pos = text.find('DOB')
    if dob_pos < 0:
        dob_pos = text.find('Date of Birth')
    
    search_text = text[:dob_pos] if dob_pos > 0 else text[:2000]
    print(f"=== NAME SEARCH AREA (before DOB, {len(search_text)} chars) ===")
    print(search_text)
    print("=== END NAME SEARCH AREA ===")
    
    # FIRST: Extract Full Name from MVR - Ontario format: "Name: LASTNAME,FIRSTNAME,MIDDLE Birth Date: ..."
    # Method 1: Direct match for "Name: " followed by text until "Birth Date" or newline
    name_match = re.search(r'Name\s*:\s*([^\n]+?)(?=\s+(?:Birth|Gender|Address|Height|Demerit)|\n)', text, re.IGNORECASE)
    if name_match:
        name_raw = name_match.group(1).strip()
        # Name format is: LASTNAME,FIRSTNAME,MIDDLE
        # Convert to: FIRSTNAME LASTNAME MIDDLE (or just use as-is if preferred)
        if ',' in name_raw:
            parts = [p.strip() for p in name_raw.split(',')]
            # Reorder: parts[0]=LASTNAME, parts[1]=FIRSTNAME, parts[2]=MIDDLE (if exists)
            if len(parts) >= 2:
                name_formatted = f"{parts[1]} {parts[0]}"
                if len(parts) > 2 and parts[2]:
                    name_formatted += f" {parts[2]}"
                data['name'] = name_formatted
                print(f" ✓ Found Name (formatted from comma-separated): {data['name']}")
            else:
                data['name'] = name_raw
                print(f" ✓ Found Name (raw): {data['name']}")
        else:
            data['name'] = name_raw
            print(f" ✓ Found Name (raw): {data['name']}")
    
    if 'name' not in data:
        print(f" ⚠️  WARNING: Could not extract name from MVR")
    else:
        print(f" ✓ FINAL NAME EXTRACTED: {data['name']}")
    
    # License Number - various patterns
    
    # License Number - various patterns
    license_patterns = [
        r'Licence Number:\s*([A-Z0-9\-]+)',  # MVR format
        r'License\s*(?:Number|#|No\.?)?[:\s]+([A-Z0-9\-]+)',
        r'DL\s*(?:Number|#|No\.?)?[:\s]+([A-Z0-9\-]+)',
        r'Driver[\'s]?\s*License[:\s]+([A-Z0-9\-]+)'
    ]
    for pattern in license_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['license_number'] = match.group(1).strip()
            print(f" Found License Number: {data['license_number']}")
            break
    
    # Expiry Date - MVR format: "Expiry Date: 03/02/2030"
    # NOTE: This is the DRIVER'S LICENSE expiry date, NOT the policy renewal date
    # Renewal date should only come from DASH PDF (Policy #1 Expiry Date)
    expiry_patterns = [
        r'Expiry Date:\s*(\d{1,2}/\d{1,2}/\d{4})',  # MVR format - driver's license expiry
        r'Expir(?:y|ation)\s*Date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'Exp\.?\s*Date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'Valid\s*(?:Through|Until)[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
    ]
    for pattern in expiry_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['expiry_date'] = normalize_date(match.group(1))
            print(f" Found License Expiry Date: {data['expiry_date']}")
            # DO NOT override renewal_date here - it should only come from DASH PDF
            # The expiry_date here is the driver's license expiry, not policy renewal
            break
    
    # Date of Birth - MVR format: "Birth Date: 03/02/1980"
    dob_patterns = [
        r'Birth Date:\s*(\d{1,2}/\d{1,2}/\d{4})',  # MVR format
        r'(?:Date\s*of\s*)?Birth\s*Date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'DOB[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'Born[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
    ]
    for pattern in dob_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['dob'] = normalize_date(match.group(1))
            print(f" Found DOB: {data['dob']}")
            break
    
    # Issue Date - MVR format: "Issue Date: 16/11/2001"
    issue_patterns = [
        r'Issue Date:\s*(\d{1,2}/\d{1,2}/\d{4})',  # MVR format
        r'Issue\s*Date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'Issued[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
    ]
    for pattern in issue_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['issue_date'] = normalize_date(match.group(1))
            print(f" Found Issue Date: {data['issue_date']}")
            break
    
    # License Status - MVR format: "Status: LICENCED"
    status_patterns = [
        r'Status:\s*(LICENCED|LICENSED|VALID|ACTIVE|SUSPENDED|REVOKED|EXPIRED)',  # MVR format
        r'Status[:\s]+(Valid|Suspended|Revoked|Expired)',
        r'License\s*Status[:\s]+(Valid|Suspended|Revoked|Expired)'
    ]
    for pattern in status_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            status = match.group(1).strip().upper()
            # Normalize "LICENCED" to "Valid"
            if status in ['LICENCED', 'LICENSED', 'ACTIVE']:
                data['license_status'] = 'Valid'
            else:
                data['license_status'] = status.capitalize()
            print(f" Found License Status: {data['license_status']}")
            break
    
    # Class/Type - MVR format: "Class: G***"
    class_patterns = [
        r'Class:\s*([A-Z0-9\*]+)',  # MVR format
        r'Class[:\s]+([A-Z0-9]+)',
        r'License\s*Class[:\s]+([A-Z0-9]+)',
        r'Type[:\s]+([A-Z0-9]+)'
    ]
    for pattern in class_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['license_class'] = match.group(1).strip().replace('*', '')
            print(f" Found License Class: {data['license_class']}")
            break
    
    # VIN and Vehicle info: Extract ALL VEHICLES from Policy #1 section (for MVR PDFs)
    # Find Policy #1, then extract up to Policy #2 (or end if no Policy #2)
    policy1_pos = text.find('Policy #1')
    policy1_vehicles_list = []  # Array to store ALL vehicles from Policy #1
    
    print(f"\n[VEHICLES] Searching for 'Policy #1' in MVR...")
    print(f"[VEHICLES] policy1_pos = {policy1_pos}")
    
    if policy1_pos >= 0:
        # Find the NEXT policy number after Policy #1
        remaining_text = text[policy1_pos + len('Policy #1'):]
        next_policy_match = re.search(r'Policy\s*#(\d+)', remaining_text)
        
        if next_policy_match:
            # Policy #1 section ends where the next policy begins
            next_policy_pos = policy1_pos + len('Policy #1') + next_policy_match.start()
            policy1_section = text[policy1_pos:next_policy_pos]
            print(f"[VEHICLES] Found next policy, Policy #1 section size: {len(policy1_section)} chars")
        else:
            # No next policy, take the rest of the document
            policy1_section = text[policy1_pos:]
            print(f"[VEHICLES] No next policy found, taking rest of doc. Policy #1 section size: {len(policy1_section)} chars")
        
        # Extract ALL vehicles from Policy #1
        # Format: "Vehicle #N: YEAR MAKE - MODEL VIN"
        # Find all occurrences of "Vehicle #N:" followed by content until next "Vehicle #" or end
        vehicle_pattern = r'Vehicle\s*#(\d+):\s*([^\n]*(?:\n(?!Vehicle\s*#).*)*)'
        vehicle_matches = re.finditer(vehicle_pattern, policy1_section, re.IGNORECASE)
        
        print(f"[VEHICLES] Searching for vehicles with pattern...")
        
        for match in vehicle_matches:
            vehicle_num = match.group(1).strip()
            vehicle_content = match.group(2)
            
            print(f"\n[VEHICLES] Processing Vehicle #{vehicle_num}...")
            print(f"[VEHICLES] Content (first 300 chars): {vehicle_content[:300]}")
            
            # Check if this is a role label (e.g., "Principal Operator", "Named Insured")
            first_line = vehicle_content.split('\n')[0].strip()
            if re.match(r'^(Principal Operator|Named Insured|Self|Spouse|Relationship|Owner)', first_line, re.IGNORECASE):
                print(f"[VEHICLES] Skipping - this is a role assignment, not a vehicle")
                continue
            
            # Try to extract VIN and year/make/model
            vin = None
            year_make_model = None
            
            # Pattern 1: "YEAR MAKE - MODEL VIN" (VIN is 17 chars, on same line)
            match1 = re.search(r'(\d{4}\s+[A-Z]+(?:\s*-\s*[^\-\n]+)?)\s*-\s*([A-HJ-NPR-Z0-9]{17})', vehicle_content, re.IGNORECASE)
            if match1:
                year_make_model = match1.group(1).strip()
                vin = match1.group(2).strip().upper()
                print(f"[VEHICLES] Pattern 1: Found year/make/model: {year_make_model}, VIN: {vin}")
            
            # Pattern 2: "YEAR MAKE - MODEL\nVIN" (VIN on next line)
            if not vin:
                match2 = re.search(r'(\d{4}\s+[A-Z]+(?:\s*-\s*[^\-\n]+)?)\s*\n\s*([A-HJ-NPR-Z0-9]{17})', vehicle_content, re.IGNORECASE)
                if match2:
                    year_make_model = match2.group(1).strip()
                    vin = match2.group(2).strip().upper()
                    print(f"[VEHICLES] Pattern 2: Found year/make/model: {year_make_model}, VIN: {vin}")
            
            # Pattern 3: Extract first meaningful line and look for VIN anywhere
            if not vin:
                lines = [l.strip() for l in vehicle_content.split('\n') if l.strip()]
                for line in lines[:3]:  # Check first 3 lines
                    vin_match = re.search(r'([A-HJ-NPR-Z0-9]{17})', line)
                    if vin_match:
                        vin = vin_match.group(1).strip().upper()
                        year_make_model = line[:vin_match.start()].strip()
                        print(f"[VEHICLES] Pattern 3: Found year/make/model: {year_make_model}, VIN: {vin}")
                        break
            
            if vin and year_make_model:
                # Clean up the year/make/model
                year_make_model = re.sub(r'\s+', ' ', year_make_model)
                year_make_model = year_make_model.rstrip(' -/:').strip()
                
                # Skip if empty
                if year_make_model and len(year_make_model) > 3:
                    policy1_vehicles_list.append({
                        'vehicle_number': vehicle_num,
                        'vin': vin,
                        'year_make_model': year_make_model
                    })
                    print(f"[VEHICLES] [OK] Added Vehicle #{vehicle_num}: {year_make_model} | VIN: {vin}")
                else:
                    print(f"[VEHICLES] Skipped - year/make/model too short: '{year_make_model}'")
            else:
                print(f"[VEHICLES] [WARN] Could not extract VIN or year/make/model for Vehicle #{vehicle_num}")
    else:
        print("[VEHICLES] [ERROR] Policy #1 not found in MVR PDF")
    
    print(f"\n[VEHICLES] FINAL RESULT: {len(policy1_vehicles_list)} vehicles extracted")
    print(f"[VEHICLES] policy1_vehicles_list = {policy1_vehicles_list}")
    
    # Store all vehicles from Policy #1 for frontend to render
    data['policy1_vehicles'] = policy1_vehicles_list
    
    # For backward compatibility, set single vehicle fields (use first vehicle if available)
    if policy1_vehicles_list:
        data['vin'] = policy1_vehicles_list[0]['vin']
        data['vehicle_year_make_model'] = policy1_vehicles_list[0]['year_make_model']
    
    # Demerit Points - MVR format: "Demerit Points: 00"
    points_patterns = [
        r'Demerit Points:\s*(\d+)',  # MVR format
        r'(?:Demerit\s*)?Points?[:\s]+(\d+)',
        r'Point\s*Balance[:\s]+(\d+)',
        r'Total\s*Points[:\s]+(\d+)'
    ]
    for pattern in points_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['demerit_points'] = match.group(1)
            print(f" Found Demerit Points: {data['demerit_points']}")
            break
    
    # Conditions/Restrictions - MVR format: "Conditions: */N"
    conditions_patterns = [
        r'Conditions:\s*([^\n]+)',  # MVR format
        r'Conditions?[:\s]+([^\n]+)'
    ]
    for pattern in conditions_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            cond = match.group(1).strip()
            # Skip if it's just */N or similar placeholder
            if cond and cond not in ['*/N', '*', 'N', 'None', 'NONE']:
                data['conditions'] = cond
                print(f" Found Conditions: {data['conditions']}")
            break
    
    # Number of Convictions - MVR format: "***Number of Convictions: 0 ***"
    convictions_pattern = r'\*+\s*Number of Convictions:\s*(\d+)\s*\*+'
    conv_match = re.search(convictions_pattern, text, re.IGNORECASE)
    if conv_match:
        conv_count = int(conv_match.group(1))
        data['convictions_count'] = str(conv_count)
        print(f" Found Convictions Count: {conv_count}")
        
        # If there are convictions, try to extract them
        if conv_count > 0:
            convictions = []
            
            # Find the "DATE CONVICTIONS, DISCHARGES AND OTHER ACTIONS" section (or similar)
            # This section typically contains the actual conviction details
            conv_section = None
            
            # Try to find "DATE CONVICTIONS" or similar header
            conv_header_match = re.search(r'DATE\s+CONVICTIONS.*?\n(.*?)(?=\*{3,}|END OF REPORT|Licence Number|^$)', text, re.IGNORECASE | re.DOTALL | re.MULTILINE)
            
            if conv_header_match:
                conv_section = conv_header_match.group(1)
            else:
                # Fallback: look from the "Number of Convictions" match onwards
                conv_section_start = conv_match.end()
                # Look for the next section header or end of document
                next_section = re.search(r'(?:^\*+|^[A-Z\*]{3,}|END OF REPORT)', text[conv_section_start:], re.MULTILINE | re.IGNORECASE)
                if next_section:
                    conv_section = text[conv_section_start:conv_section_start + next_section.start()]
                else:
                    conv_section = text[conv_section_start:]
            
            print(f"\n=== CONVICTIONS SECTION (First 2000 chars) ===")
            print(conv_section[:2000] if conv_section else "NO SECTION FOUND")
            print(f"=== END CONVICTIONS SECTION ===\n")
            
            # Try multiple patterns to extract conviction details
            # Pattern 1: Standard MVR format - lines with date, offense, and penalties
            # Looking for patterns like:
            # 01/15/2023 Speeding 20+ km/h over limit Fine: $280
            # Or: 01/15/2023 - Speeding...
            # Or: DISOBEY LEGAL SIGN / OFFENCE DATE 2024/12/28 (multi-line format)
            
            conv_detail_patterns = [
                # Multi-line format: Description on one line, OFFENCE DATE on next
                r'([A-Za-z\s\-\(\)0-9\.&/]+?)\s*\n\s*OFFENCE\s+DATE\s+(\d{1,2}/\d{1,2}/\d{4})',
                # Date + offense + fine (most common MVR format)
                r'(\d{1,2}/\d{1,2}/\d{4})\s+([A-Za-z\s\-\(\)0-9\.&/]+?)(?:\s+Fine:\s*\$?[\d,.]+|\s+Penalty.*)?(?:\n|$)',
                # Date - description format
                r'(\d{1,2}/\d{1,2}/\d{4})\s*[\-]\s*([A-Za-z\s\-\(\)0-9\.&/]+?)(?:\n|$)',
                # Numbered conviction format: 1. Date Description
                r'^\s*\d+\.\s+(\d{1,2}/\d{1,2}/\d{4})\s+([A-Za-z\s\-\(\)0-9\.&/]+?)$',
                # Conviction list format with newlines separating offense from fine
                r'(\d{1,2}/\d{1,2}/\d{4})\s*\n\s*([A-Za-z\s\-\(\)0-9\.&/]+?)(?=\n\d{1,2}/\d{1,2}/\d{4}|\n---|\n\*|\Z)',
            ]
            
            for pattern in conv_detail_patterns:
                print(f"\n[PATTERN] Trying pattern: {pattern[:80]}...")
                conv_matches = re.finditer(pattern, conv_section, re.IGNORECASE | re.MULTILINE)
                matched_count = 0
                
                for match in conv_matches:
                    # Handle both formats: (date, description) and (description, date)
                    if 'OFFENCE' in pattern or 'OFFENCE' in match.group(0):
                        # Format: description first, date second
                        description = match.group(1).strip()
                        date_str = match.group(2).strip()
                    else:
                        # Format: date first, description second
                        date_str = match.group(1).strip()
                        description = match.group(2).strip()
                    
                    # Clean up description - remove extra whitespace and common artifacts
                    description = re.sub(r'\s+', ' ', description)
                    description = re.sub(r'\s*[Ff]ine:\s*\$?[\d,.]+\s*', '', description)
                    description = re.sub(r'\s*[Pp]enalty.*?$', '', description, flags=re.MULTILINE)
                    description = description.strip()
                    
                    # Skip if description is empty or just punctuation
                    if description and description not in ['', '-', '*', 'N', 'None', 'NONE'] and len(description) > 2:
                        conviction = {
                            'date': normalize_date(date_str),
                            'description': description
                        }
                        # Avoid duplicates
                        if conviction not in convictions:
                            convictions.append(conviction)
                            matched_count += 1
                            print(f"   Found: {conviction['date']} - {conviction['description'][:60]}...")
                
                # If we found enough convictions with this pattern, use it
                if len(convictions) >= conv_count:
                    print(f" Pattern matched {matched_count} convictions, stopping pattern search")
                    break
                elif matched_count > 0:
                    print(f" Pattern matched {matched_count} conviction(s)")
            
            if convictions:
                data['convictions'] = convictions
                print(f"\n[OK] Extracted {len(convictions)} conviction details out of {conv_count} expected")
                if len(convictions) < conv_count:
                    print(f"[WARNING]  Note: Expected {conv_count} but found {len(convictions)} - PDF format may vary")
            else:
                # If we couldn't extract details, at least show count
                print(f"[WARNING]  Could not extract conviction details (found count: {conv_count})")
                print(f"    This might be due to PDF format variation. Please check the PDF manually.")
    else:
        # Default to 0 if not found
        data['convictions_count'] = '0'
        print(f" No convictions section found (defaulting to 0 convictions)")
    
    print(f"=== MVR EXTRACTED DATA ===")
    print(json.dumps(data, indent=2))
    print(f"=== END DATA ===")
    
    # CRITICAL: Verify policy1_vehicles is in the data being returned
    print(f"\n[VERIFY] About to return extract_mvr_fields data:")
    print(f"[VERIFY] - 'policy1_vehicles' key exists: {'policy1_vehicles' in data}")
    if 'policy1_vehicles' in data:
        print(f"[VERIFY] - policy1_vehicles value: {data['policy1_vehicles']}")
        print(f"[VERIFY] - policy1_vehicles length: {len(data['policy1_vehicles'])}")
    print(f"[VERIFY] - Total data keys: {len(data)}")
    
    return data


def normalize_date(date_str):
    """
    Convert various date formats to MM/DD/YYYY
    """
    try:
        # Try different date formats
        formats = [
            '%m/%d/%Y', '%m-%d-%Y',
            '%m/%d/%y', '%m-%d-%y',
            '%d/%m/%Y', '%d-%m-%Y',
            '%Y-%m-%d', '%Y/%m/%d'
        ]
        
        for fmt in formats:
            try:
                date_obj = datetime.strptime(date_str, fmt)
                return date_obj.strftime('%m/%d/%Y')
            except ValueError:
                continue
        
        return date_str  # Return original if no format matches
    except:
        return date_str
