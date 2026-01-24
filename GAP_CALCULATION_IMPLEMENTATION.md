# Gap Calculation Implementation - Multiple Adjacent Policy Pairs

## Summary of Changes

This implementation fulfills the strict requirement to show **gap calculations for ALL ADJACENT POLICY PAIRS**, where for N policies, exactly (N-1) gap sections are displayed.

## Key Requirements Met

### ✅ Core Functionality
- **Gap Sections**: For N policies, exactly (N-1) gap calculation sections are rendered
- **Adjacent Pairs Only**: Each section compares Policy[i] with Policy[i-1]
- **No Sorting**: Policies are processed in the exact order provided by the data source (PDF)
- **Dynamic Rendering**: Gap sections automatically render when policies are extracted

### ✅ Field Mapping (Per Specification)
- **START OF TERM**: CURRENT policy's End of the Latest Term (Policy[i].end_date)
- **PREV EXPIRE**: PREVIOUS policy's Start of the Earliest Term (Policy[i-1].start_date)
- **INSURANCE GAP**: Gap calculation result

### ✅ Gap Calculation Logic
For each adjacent pair:
```
Gap = (CURRENT policy End Date) - (PREVIOUS policy Start Date)
```
Result display:
- If gap == 0 days → "0 Days" (slate-700)
- If gap > 0 days → "Gap (X Days)" (rose-600)
- If gap < 0 days → "Overlap (|X| Days)" (amber-600)
- If dates missing → "-" (slate-700)

### ✅ Edge Cases Handled
- **Fewer than 2 policies**: Displays message "No policies available or fewer than 2 policies to calculate gaps"
- **Missing dates**: Shows "-" for that field, other sections still render
- **Invalid dates**: Skips gap calculation for that section, shows "-"

## Files Modified

### 1. `Auto dashboard.html`

#### Changes:
1. **Replaced old single gap section (Lines ~414-426)** with dynamic container:
   ```html
   <div id="gap-sections-container">
       <!-- Gap sections will be dynamically rendered here -->
   </div>
   ```

2. **Added new `renderGapSections()` function** (Lines ~1880-1955):
   - Creates N-1 sections for N policies
   - Iterates from last policy down to first: `for (let i = policyCount - 1; i > 0; i--)`
   - Compares adjacent pairs: Policy[i] with Policy[i-1]
   - Calculates gap in days using: `Math.ceil(diffTime / (1000 * 60 * 60 * 24))`
   - Displays appropriate gap message (0 Days, Gap, or Overlap)
   - Renders read-only input fields with styling

3. **Updated `refreshUI()` function** (Line ~797):
   - Calls `this.renderGapSections()` to dynamically render all gap sections
   - Removed old single gap field handling

4. **Removed deprecated event handler** (Line ~795):
   - Old single gap calculation triggered on field change is removed
   - Gap sections are now read-only and auto-rendered

### 2. `backend/pdf_parser.py`

#### Changes:
1. **Removed policy sorting** (Line ~282):
   - **Before**: `all_policies.sort(key=lambda x: x['number'])`
   - **After**: No sorting - policies maintain order from PDF
   
2. **Updated comments** to document the strict requirement:
   ```python
   # IMPORTANT: Preserve the order from the PDF (data source) - DO NOT SORT
   # The order of appearance in the PDF is the only source of truth
   data['all_policies'] = all_policies
   ```

3. **Adjusted first insurance date logic**:
   - Uses first policy in the list (not necessarily Policy #1)
   - Ensures the order from data source is respected

## Example Scenarios

### Scenario 1: 2 Policies
Input policies (in order):
- Policy[0]: 2025-01-01 to 2025-12-31
- Policy[1]: 2026-01-01 to 2026-12-31

Output: 1 gap section
- Gap Section #1:
  - START OF TERM: 2026-12-31 (Policy[1] end)
  - PREV EXPIRE: 2025-01-01 (Policy[0] start)
  - INSURANCE GAP: Gap (365 Days)

### Scenario 2: 6 Policies
Input policies (in order):
- Policy[0] through Policy[5]

Output: 5 gap sections
- Gap Section #1: Policy[5] ← Policy[4]
- Gap Section #2: Policy[4] ← Policy[3]
- Gap Section #3: Policy[3] ← Policy[2]
- Gap Section #4: Policy[2] ← Policy[1]
- Gap Section #5: Policy[1] ← Policy[0]

## Compliance Checklist

- ✅ No hardcoded indexes
- ✅ No assumptions on policy count
- ✅ No sorting or reordering
- ✅ Uses data source order exclusively
- ✅ Dynamic N-1 sections for N policies
- ✅ Adjacent pairs only
- ✅ Correct field mapping
- ✅ Proper gap calculation in days
- ✅ Edge cases handled
- ✅ Read-only rendering (no user input required)

## Testing Recommendations

1. **Upload DASH PDF with 2 policies** → Verify 1 gap section renders
2. **Upload DASH PDF with 6 policies** → Verify 5 gap sections in correct order
3. **Upload DASH PDF with 1 policy** → Verify message "No policies available..."
4. **Verify policy order** → Check console logs show "NO SORTING"
5. **Check gap calculations** → Manually verify day difference calculations

## Technical Notes

- All gap sections are read-only (no user input possible)
- Sections render automatically when DASH PDF is uploaded via `refreshUI()`
- Policy order is logged to console for debugging
- Each section shows its position and comparison (e.g., "Gap Section #3: Position 3 ← Position 2")
