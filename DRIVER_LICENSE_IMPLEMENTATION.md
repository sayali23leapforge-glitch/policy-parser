# Driver License Received Answer Display - Implementation

## Overview
Changed the META Leads Manager dashboard to display the answer to "When did you first receive your G or G2 driver's licence?" instead of the lead ID in the badge.

## Changes Made

### 1. **Database Schema** (`supabase_schema.sql`)
- Added new column: `driver_license_received VARCHAR(255)`
- Stores the answer to the custom form question

### 2. **Backend** (`backend/app.py`)
- Modified `parse_meta_lead()` function to extract driver license answer
- Searches for the question answer using multiple possible field names:
  - `when did you first receive your g or g2 driver's licence?`
  - `when did you first receive your g or g2 drivers licence?`
  - `driver license received`
  - `g or g2 driver license`
  - `driver_license_received`
- Falls back to empty string if not found

### 3. **Frontend** (`meta dashboard.html`)
- Modified `_renderLeadBadge()` function
- **New Logic:**
  - If lead is manual → Show "Manual Lead" (yellow badge)
  - If driver_license_received has value → Show the answer (indigo badge)
  - If no answer → Show ID as fallback (slate badge)

## How It Works

1. **Meta Lead Form** collects the question "When did you first receive your G or G2 driver's licence?"
2. **Backend** receives the lead and extracts this answer
3. **Database** stores it in `driver_license_received` column
4. **Dashboard** displays the answer in a styled badge instead of the ID

## Display Examples

| Scenario | Badge Display |
|----------|---------------|
| Manual Lead | "Manual Lead" (yellow) |
| 2021 or later | "2021 or later" (indigo) |
| 2020 or before | "2020 or before" (indigo) |
| No answer provided | "ID: #123" (slate) |

## Migration Steps

1. **Run the SQL migration** to add the column:
   ```sql
   ALTER TABLE leads
   ADD COLUMN IF NOT EXISTS driver_license_received VARCHAR(255);
   ```

2. **Restart the backend** to apply the code changes:
   ```bash
   python run.py
   ```

3. **Test** by uploading a new lead from Meta that includes the driver license question answer

## Fallback Behavior
- If the `driver_license_received` field is not found, it safely falls back to displaying the lead ID
- The system is backward compatible with existing leads

## Future Enhancements
- Can filter/sort by driver license received answer
- Can add to lead scoring algorithm
- Can display multiple custom answers if needed
