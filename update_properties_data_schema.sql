-- Update properties_data table to support lead name/phone search
-- Run this in Supabase SQL Editor if the table already exists

-- Add new columns if they don't exist
DO $$
BEGIN
    -- Add lead_name column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='properties_data' AND column_name='lead_name') THEN
        ALTER TABLE properties_data ADD COLUMN lead_name VARCHAR(255);
        RAISE NOTICE 'Added lead_name column';
    END IF;
    
    -- Add lead_phone column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='properties_data' AND column_name='lead_phone') THEN
        ALTER TABLE properties_data ADD COLUMN lead_phone VARCHAR(20);
        RAISE NOTICE 'Added lead_phone column';
    END IF;
    
    -- Add customer JSONB column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='properties_data' AND column_name='customer') THEN
        ALTER TABLE properties_data ADD COLUMN customer JSONB;
        RAISE NOTICE 'Added customer column';
    END IF;
END $$;

-- Create index on lead_name for faster queries
CREATE INDEX IF NOT EXISTS idx_properties_data_lead_name ON properties_data(lead_name);

-- Display success message
SELECT 'Schema update completed successfully!' AS status;
