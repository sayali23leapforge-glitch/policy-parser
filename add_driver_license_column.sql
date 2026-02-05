-- Migration: Add driver_license_received column to leads table
-- This column stores the answer to "When did you first receive your G or G2 driver's licence?"

ALTER TABLE leads
ADD COLUMN IF NOT EXISTS driver_license_received VARCHAR(255);

-- Create an index for faster filtering if needed
CREATE INDEX IF NOT EXISTS idx_leads_driver_license ON leads(driver_license_received);

-- Verify the column was added
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'leads' AND column_name = 'driver_license_received';
