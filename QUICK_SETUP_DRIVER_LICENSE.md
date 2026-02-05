# Quick Start: Display Driver License Answer on META Dashboard

## What Changed?
Instead of showing the lead ID (e.g., "ID: #123"), the META dashboard now displays the answer to "When did you first receive your G or G2 driver's licence?" in a colored badge.

## Setup Instructions

### Step 1: Update Database Schema
Run this SQL in your Supabase console:

```sql
ALTER TABLE leads
ADD COLUMN IF NOT EXISTS driver_license_received VARCHAR(255);

CREATE INDEX IF NOT EXISTS idx_leads_driver_license ON leads(driver_license_received);
```

### Step 2: Restart Backend
Stop and restart your Flask backend:

```bash
# Kill current process
Ctrl+C

# Restart
python run.py
```

### Step 3: Test It Out
1. Go to your Meta Lead Form
2. Submit a lead with the answer to "When did you first receive your G or G2 driver's licence?"
3. Check the META dashboard - you should see the answer in the badge instead of the ID

## Display Examples

```
Lead 1: Shows "2021 or later" (indigo badge) ✓
Lead 2: Shows "2020 or before" (indigo badge) ✓
Lead 3: Shows "Manual Lead" (yellow badge) - manually added lead
Lead 4: Shows "ID: #456" (slate badge) - fallback if no answer provided
```

## What Was Modified?

| File | Change |
|------|--------|
| `supabase_schema.sql` | Added `driver_license_received` column |
| `backend/app.py` | Extract driver license answer from Meta form data |
| `meta dashboard.html` | Display answer in badge instead of ID |

## Features
✅ Automatic extraction from Meta form responses
✅ Fallback to ID if answer not provided
✅ Special handling for manual leads
✅ Styled with indigo badge for easy visibility
✅ Backward compatible with existing leads

## Troubleshooting

**Q: I still see the ID instead of the answer**
A: Make sure you:
1. Restarted the backend after code changes
2. The Meta form question field name matches one of these:
   - "When did you first receive your G or G2 driver's licence?"
   - "When did you first receive your G or G2 drivers licence?"
   - "Driver license received"
   - "G or G2 driver license"

**Q: New leads aren't showing the answer**
A: Run the SQL migration to add the column if you haven't already.

## Need Help?
Check `DRIVER_LICENSE_IMPLEMENTATION.md` for detailed technical information.
